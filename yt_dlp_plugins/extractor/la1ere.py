import functools
import re

from yt_dlp.extractor.common import InfoExtractor
from yt_dlp.extractor.francetv import FranceTVInfoIE as _FranceTVInfoIE
from yt_dlp.utils import (
    ExtractorError,
    OnDemandPagedList,
    int_or_none,
    js_to_json,
    orderedSet,
    parse_iso8601,
    url_or_none,
)
from yt_dlp.utils.traversal import traverse_obj


class FranceTVInfoIE(_FranceTVInfoIE):
    # /programme-audio/ paths handled by FranceTVInfoLa1ereAudioIE below
    _VALID_URL = r'https?://(?:www|mobile|france3-regions|la1ere)\.france(?:tv)?info\.fr/(?!(?:[^/?#]+/)*programme-audio/)(?:[^/?#]+/)*(?P<id>[^/?#&.]+)'

    def _real_extract(self, url):
        try:
            return super()._real_extract(url)
        except ExtractorError:
            if 'la1ere.franceinfo.fr' not in url:
                raise

        display_id = self._match_id(url)
        webpage = self._download_webpage(url, display_id)

        # la1ere falls back to inline JS data: a 'diffusion:{...}' block on
        # single-episode pages, or the 'article:{...}' object on articles.
        # Related articles and the replay widget carry videoId fields too,
        # so only the article's own mainMedia and bodyMediaList are used
        diffusion_id = self._search_regex(
            r'\bdiffusion:\{[^{}]*videoId:"([\da-f]{8}-[\da-f]{4}-[\da-f]{4}-[\da-f]{4}-[\da-f]{12})"',
            webpage, 'diffusion video id', default=None)
        if diffusion_id:
            return self._make_url_result(diffusion_id, url=url)
        article = self._search_json(
            r'\barticle\s*:', webpage, 'article data', display_id,
            transform_source=js_to_json, default={})
        video_ids = orderedSet(traverse_obj(article, (
            ('mainMedia', ('bodyMediaList', ...)), 'videoId', {str})))
        if not video_ids:
            raise ExtractorError('Unable to extract video id', expected=True)
        if len(video_ids) == 1:
            return self._make_url_result(video_ids[0], url=url)
        return self.playlist_result(
            [self._make_url_result(vid, url=url) for vid in video_ids],
            playlist_id=display_id)


class FranceTVInfoLa1ereAudioIE(InfoExtractor):
    IE_NAME = 'franceinfo:la1ere:audio'
    IE_DESC = 'la1ere.franceinfo.fr audio podcast series'
    _VALID_URL = r'https?://la1ere\.franceinfo\.fr/[^/?#]+/programme-audio/(?P<display_id>[^/?#]+-(?P<id>\d+))/?'

    def _fetch_page(self, series_id, page):
        episodes = self._download_json(
            f'https://la1ere.franceinfo.fr/api/audio/podcasts/{series_id}/episodes',
            series_id, f'Downloading episodes page {page + 1}',
            query={'page': page + 1}, fatal=False) or []
        for episode in episodes:
            feed_url = traverse_obj(episode, ('feed', {url_or_none}))
            episode_id = episode.get('id')
            if not feed_url or not episode_id:
                continue
            yield {
                'id': str(episode_id),
                'url': feed_url,
                'ext': 'mp3',
                'vcodec': 'none',
                'title': episode.get('title'),
                'description': episode.get('description'),
                'duration': int_or_none(episode.get('duration')),
                'timestamp': parse_iso8601(episode.get('broadcastDate')),
                'thumbnail': traverse_obj(episode, ('thumbnail', 'src', {url_or_none})),
            }

    def _real_extract(self, url):
        display_id, series_id = self._match_valid_url(url).group('display_id', 'id')

        webpage = self._download_webpage(url, display_id, fatal=False) or ''
        title = (
            self._html_search_meta(['og:title', 'twitter:title'], webpage, default=None)
            or self._html_extract_title(webpage, default=None))
        if title:
            title = re.sub(r'\s+à\s+\(ré\)écouter\s+sur.*$', '', title).strip(' .') or None

        entries = OnDemandPagedList(functools.partial(self._fetch_page, series_id), 8)

        return self.playlist_result(entries, playlist_id=series_id, playlist_title=title)

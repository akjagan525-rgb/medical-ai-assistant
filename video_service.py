import urllib.request
import urllib.parse
import re

def get_video_url_for_disease(query_text: str, language: str = "Tamil") -> str:
    """
    Performs a 100% dynamic search for ANY condition or question,
    using the lightweight mobile endpoint for maximum speed.
    """
    fallback_url = "https://www.youtube.com/watch?v=ReYRmcF26v0" if language.lower() == "tamil" else "https://www.youtube.com/watch?v=5Ujh7p6u3mE"
    
    try:
        # Build search query
        if language.lower() == "tamil":
            search_query = f"{query_text} மருத்துவம் விளக்கம் causes symptoms in tamil"
        else:
            search_query = f"{query_text} medical causes pathophysiology animation"

        encoded = urllib.parse.quote(search_query)
        # Query YouTube mobile search (10x lighter and faster than desktop)
        url = f"https://m.youtube.com/results?search_query={encoded}"

        req = urllib.request.Request(
            url,
            headers={
                "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 16_5 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.5 Mobile/15E148 Safari/604.1"
            }
        )

        with urllib.request.urlopen(req, timeout=3.0) as response:
            # Reads only the first 60KB to extract the top video instantly
            html_chunk = response.read(60000).decode('utf-8', errors='ignore')
            video_ids = re.findall(r"/watch\?v=([a-zA-Z0-9_-]{11})", html_chunk)

            if video_ids:
                return f"https://www.youtube.com/watch?v={video_ids[0]}"

    except Exception as e:
        print(f"Video search error: {e}")

    return fallback_url

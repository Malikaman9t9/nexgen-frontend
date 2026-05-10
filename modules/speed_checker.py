import requests
import concurrent.futures

def fetch_strategy_data(url, strategy, api_key):
    base_url = "https://www.googleapis.com/pagespeedonline/v5/runPagespeed"
    
    params = {
        'url': url,
        'strategy': strategy,
        'key': api_key,
        'category': ['performance', 'accessibility', 'best-practices', 'seo']
    }
    
    # Default fallback data structure
    fallback_data = {
        'performance': 0, 'accessibility': 0, 'best-practices': 0, 'seo': 0,
        'metrics': {
            'fcp': {'value': 'N/A', 'score': 0}, 'lcp': {'value': 'N/A', 'score': 0},
            'tbt': {'value': 'N/A', 'score': 0}, 'cls': {'value': 'N/A', 'score': 0},
            'si': {'value': 'N/A', 'score': 0}
        }
    }
    
    try:
        response = requests.get(base_url, params=params, timeout=60)
        if response.status_code == 200:
            data = response.json()
            cats = data.get('lighthouseResult', {}).get('categories', {})
            audits = data.get('lighthouseResult', {}).get('audits', {})
            
            def get_audit(key):
                return {
                    'value': audits.get(key, {}).get('displayValue', 'N/A'),
                    'score': audits.get(key, {}).get('score', 0)
                }

            return strategy, {
                'performance': int(cats.get('performance', {}).get('score', 0) * 100) if cats.get('performance', {}).get('score') else 0,
                'accessibility': int(cats.get('accessibility', {}).get('score', 0) * 100) if cats.get('accessibility', {}).get('score') else 0,
                'best-practices': int(cats.get('best-practices', {}).get('score', 0) * 100) if cats.get('best-practices', {}).get('score') else 0,
                'seo': int(cats.get('seo', {}).get('score', 0) * 100) if cats.get('seo', {}).get('score') else 0,
                'metrics': {
                    'fcp': get_audit('first-contentful-paint'),
                    'lcp': get_audit('largest-contentful-paint'),
                    'tbt': get_audit('total-blocking-time'),
                    'cls': get_audit('cumulative-layout-shift'),
                    'si': get_audit('speed-index')
                }
            }
        else:
            print(f"[-] Speed API Error ({strategy}): {response.status_code} - {response.text}")
            return strategy, fallback_data
    except Exception as e:
        print(f"[-] Speed Exception Error for {strategy}: {e}")
        return strategy, fallback_data

def check_speed(url, api_key):
    print(f"[*] Running PageSpeed API for {url}...")
    results = {}
    
    # Run Desktop and Mobile checks concurrently to save time
    with concurrent.futures.ThreadPoolExecutor(max_workers=2) as executor:
        future_mobile = executor.submit(fetch_strategy_data, url, 'mobile', api_key)
        future_desktop = executor.submit(fetch_strategy_data, url, 'desktop', api_key)
        
        strat_m, data_m = future_mobile.result()
        strat_d, data_d = future_desktop.result()
        
        results[strat_m] = data_m
        results[strat_d] = data_d

    return results
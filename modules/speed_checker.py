import requests
import time

def fetch_strategy_data(url, strategy, api_key, retries=3):
    base_url = "https://www.googleapis.com/pagespeedonline/v5/runPagespeed"
    
    params = {
        'url': url,
        'strategy': strategy,
        'category': ['performance', 'accessibility', 'best-practices', 'seo']
    }
    
    if api_key and len(api_key) > 5:
        params['key'] = api_key
        
    # Default fallback data
    fallback_data = {
        'performance': 0, 'accessibility': 0, 'best-practices': 0, 'seo': 0,
        'metrics': {
            'fcp': {'value': 'N/A', 'score': 0}, 'lcp': {'value': 'N/A', 'score': 0},
            'tbt': {'value': 'N/A', 'score': 0}, 'cls': {'value': 'N/A', 'score': 0},
            'si': {'value': 'N/A', 'score': 0}
        }
    }
    
    for attempt in range(retries):
        try:
            print(f"[*] Calling PageSpeed API for {strategy} (Attempt {attempt + 1}/{retries})...")
            # Timeout barha kar 90 sec kar diya hai taake heavy sites bhi load ho jayen
            response = requests.get(base_url, params=params, timeout=90) 
            
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
            elif response.status_code == 429:
                print(f"[-] Rate limited by Google (429). Retrying in 6 seconds...")
                time.sleep(6)
            elif response.status_code >= 500:
                print(f"[-] Google Server Error ({response.status_code}). Retrying in 5 seconds...")
                time.sleep(5)
            else:
                print(f"[-] Google API Error ({strategy}): {response.status_code} - {response.text}")
                # Agar 400 (Bad Request) aaye toh URL ya API key galat hai, seedha break karo
                break 
                
        except Exception as e:
            print(f"[-] Speed Exception Error for {strategy}: {e}")
            time.sleep(4) # Network issue ho toh 4 second wait karega
            
    return strategy, fallback_data

def check_speed(url, api_key):
    print(f"[*] Running PageSpeed Engine for {url}...")
    results = {}
    
    # 1. Check Mobile Speed
    strat_m, data_m = fetch_strategy_data(url, 'mobile', api_key)
    results[strat_m] = data_m
    
    # Delay to avoid Google API rate limits
    print("[*] Waiting 2 seconds before Desktop check to avoid Google Rate Limits...")
    time.sleep(2)
    
    # 3. Check Desktop Speed
    strat_d, data_d = fetch_strategy_data(url, 'desktop', api_key)
    results[strat_d] = data_d

    return results
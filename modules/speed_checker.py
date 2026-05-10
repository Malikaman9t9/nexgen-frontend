import requests
import time

def fetch_strategy_data(url, strategy, api_key):
    base_url = "https://www.googleapis.com/pagespeedonline/v5/runPagespeed"
    
    params = {
        'url': url,
        'strategy': strategy,
        'category': ['performance', 'accessibility', 'best-practices', 'seo']
    }
    
    # Agar API key theek hai toh hi add karein, warna Google free quota use hoga
    if api_key and len(api_key) > 5:
        params['key'] = api_key
        
    # Default fallback data (agar Google block kare)
    fallback_data = {
        'performance': 0, 'accessibility': 0, 'best-practices': 0, 'seo': 0,
        'metrics': {
            'fcp': {'value': 'N/A', 'score': 0}, 'lcp': {'value': 'N/A', 'score': 0},
            'tbt': {'value': 'N/A', 'score': 0}, 'cls': {'value': 'N/A', 'score': 0},
            'si': {'value': 'N/A', 'score': 0}
        }
    }
    
    try:
        print(f"[*] Calling PageSpeed API for {strategy}...")
        # 60 sec timeout kyunke PageSpeed analyze karne mein time leta hai
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
            print(f"[-] Google API Error ({strategy}): {response.status_code} - {response.text}")
            return strategy, fallback_data
    except Exception as e:
        print(f"[-] Speed Exception Error for {strategy}: {e}")
        return strategy, fallback_data

def check_speed(url, api_key):
    print(f"[*] Running PageSpeed Engine for {url}...")
    results = {}
    
    # Run Sequentially (Ek ke baad ek) taake Google Rate Limit na lagaye
    strat_m, data_m = fetch_strategy_data(url, 'mobile', api_key)
    results[strat_m] = data_m
    
    # 2 second ka gap taake Google server ko saans mil jaye
    print("[*] Waiting 2 seconds before Desktop check...")
    time.sleep(2)
    
    strat_d, data_d = fetch_strategy_data(url, 'desktop', api_key)
    results[strat_d] = data_d

    return results
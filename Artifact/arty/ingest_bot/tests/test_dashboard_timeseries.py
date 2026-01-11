def test_timeseries_endpoint(client):
    res = client.get('/api/report/btc/timeseries')
    assert res.status_code in (200, 404)
    if res.status_code == 200:
        j = res.get_json()
        assert 'series' in j and 'timestamps' in j['series']

import redis

# Utwórz połączenie z serwerem Redis
r = redis.Redis(host='192.168.1.22', port=6379)

r.set('foo', 'bar')

print(r.get('xxx') == None)
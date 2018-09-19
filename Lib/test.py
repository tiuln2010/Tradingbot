from time import sleep
def foo(bar, baz):
  print('started')
  print('hello {0}'.format(bar))
  sleep(2)
  print('ended')
  return 'foo' + baz

from multiprocessing.pool import ThreadPool
pool = ThreadPool()

return_val = []

async_result1 = pool.apply_async(foo, ('world', 'foo1'))
return_val.append(async_result1.get())  
async_result2 = pool.apply_async(foo, ('world', 'foo2'))
async_result3 = pool.apply_async(foo, ('world', 'foo3'))
# do some other stuff in the main process



return_val.append(async_result2.get())  
return_val.append(async_result3.get())  
print(return_val)
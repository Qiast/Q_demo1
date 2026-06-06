from langchain_core.runnables import RunnableLambda, RunnableParallel, RunnablePassthrough
from langchain_core.tracers import Run

def function(num):
    return num + 10

func = RunnableLambda(function)

result = func.invoke(3)
print(result)

# 批处理
res = func.batch([1, 2, 3])
print(res)


def separation(sentence: str):
    for word in sentence.split(' '):
        yield word

sep = RunnableLambda(separation)
stream = sep.stream("a whole village disappeared beneath a massive landslide in Switzerland")

for chunk in stream:
    print(chunk)

chain1 = RunnableParallel(r1 = func, r2 = func)
re = chain1.invoke(3, config = {"max_concurrency": 2})
print(re)

dic = RunnableLambda(lambda x: {"number": x})

print("============================================")
# RunnablePassthrough以字典为输入，返回字典
chain = dic | RunnablePassthrough.assign(new = RunnableLambda(lambda x: x["number"] + 20))
print(chain.invoke(3))

# 后备选项
print("============================================")
func2 = RunnableLambda(lambda x: int(x) + 100)
chain2 = func.with_fallbacks([func2])
print(chain2.invoke('3'))

print("============================================")
# 根据条件动态构建chain
func3 = RunnableLambda(lambda x : [x] * 3)
chain3 = func | RunnableLambda(lambda x : func3 if x > 15 else func2)
print(chain3.invoke(6))

# 生命周期监听
print("============================================")
def on_start(run_obj: Run):
    """当节点启动时，自动调用"""
    print("开始时间:", run_obj.start_time)

def on_end(run_obj: Run):
    """当节点结束时，自动调用"""
    print("结束时间:", run_obj.end_time)

chain4 = func.with_listeners(on_start = on_start, on_end = on_end)
print(chain4.invoke(3))
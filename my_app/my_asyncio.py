import asyncio

class MyAsync:
  task_list = []

  @staticmethod
  def add_task(court):
    task = MyAsync.loop().create_task(court)
    MyAsync.task_list.append(task)
  
  @staticmethod
  def release():
    if not MyAsync.task_list:
      return
    
    MyAsync.loop().run_until_complete(asyncio.wait(MyAsync.task_list))
    MyAsync.loop().close()
  
  @staticmethod
  def loop():
    try:
        return asyncio.get_event_loop()
    except RuntimeError as e:
        if e.args[0].startswith('There is no current event loop'):
            asyncio.set_event_loop(asyncio.new_event_loop())
            return asyncio.get_event_loop()
        raise e
import asyncio

class MyAsync:
  def __init__(self):
    self.task_list = []
    self.loop = MyAsync.get_loop()

  def add_task(self, court):
    if not self.loop:
      self.loop = MyAsync.get_loop()
      
    task = self.loop.create_task(court)
    self.task_list.append(task)
  
  def release(self):
    if not self.task_list or not self.loop:
      return
    
    self.loop.run_until_complete(asyncio.wait(self.task_list))
    self.loop.close()
    self.loop = None
  
  @staticmethod
  def get_loop():
    try:
        return asyncio.get_event_loop()
    except RuntimeError as e:
        if e.args[0].startswith('There is no current event loop'):
            asyncio.set_event_loop(asyncio.new_event_loop())
            return asyncio.get_event_loop()
        raise e
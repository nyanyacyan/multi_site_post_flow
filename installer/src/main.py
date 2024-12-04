#  coding: utf-8
# ----------------------------------------------------------------------------------
# 2024/6/17 更新

# ----------------------------------------------------------------------------------


import time
import asyncio


from method.base.utils import Logger
from method.flow import Flow



# ------------------------------------------------------------------------------


class Main:
   def __init__(self, debugMode=True):

      # logger
      self.getLogger = Logger(__name__, debugMode=debugMode)
      self.logger = self.getLogger.getLogger()

      self.flow = Flow(debugMode=debugMode)

   async def main(self):
      start_time = time.time()

      await self.flow.process()

      end_time = time.time()

      diff_time = end_time - start_time

      self.logger.info(f"処理時間 : {diff_time}秒")


# ------------------------------------------------------------------------------



if __name__ == '__main__':
   main_process = Main()
   asyncio.run(main_process.main())

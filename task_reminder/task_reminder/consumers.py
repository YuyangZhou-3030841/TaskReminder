from channels.generic.websocket import AsyncWebsocketConsumer
import json
class TaskConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        await self.accept()
        await self.channel_layer.group_add("tasks", self.channel_name)

    async def task_update(self, event):
        await self.send(text_data=json.dumps(event))
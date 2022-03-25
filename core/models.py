# -*- coding: utf 8 -*-
from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User

class Message(models.Model):
	emitter = models.ForeignKey(User, related_name='+')
	receiver = models.ForeignKey(User)
	date_message = models.DateTimeField(default=timezone.now)
	text = models.TextField(verbose_name='Message')
	visualized = models.BooleanField(default=False)

	def __str__(self):
		return 'Message from ' + self.emitter.first_name + ' for ' + self.receiver.first_name

	def count_messages(self, user_loged):
		return sum(
		    message[2] == False for message in self.get_users_recently(user_loged))

	def get_users_recently(self, user_loged):
		l = []

		for user_visited in User.objects.all():
			if self.get_ultimate_message(user_loged, user_visited):
				read = (self.get_ultimate_message(user_loged,
				                                  user_visited).emitter == user_loged
				        or self.get_ultimate_message(user_loged,
				                                     user_visited).visualized != False)
				l.append([user_visited, self.get_ultimate_message(user_loged, user_visited), read])
		return sorted((sorted(l, key=lambda inst: inst[1].date_message)[::-1]), key=lambda inst: inst[1].visualized)

	def get_30_messages(self, user_loged, user_visited):
		mlog = Message.objects.filter(emitter=user_loged, receiver=user_visited)
		mvis = Message.objects.filter(emitter=user_visited, receiver=user_loged)

		ms = list(mlog)
		for m in mvis:
			if m.visualized == False:
				m.visualized = True
				m.save()
			ms.append(m)

		return sorted(ms, key=lambda inst: inst.date_message)[::-1][:30][::-1]

	def format_date_chat(self, data):
		return self.less_than_10(data.day) + "/" + self.less_than_10(data.month) + "/" + str(data.year) + " at " + self.less_than_10(data.hour) + ":" + self.less_than_10(data.minute) + ":" + self.less_than_10(data.second)

	def less_than_10(self, n):
		return "0"+ str(n) if n < 10 else str(n)

	def get_all_messages(self, user_loged, user_visited):
		mlog = Message.objects.filter(emitter=user_loged, receiver=user_visited)
		mvis = Message.objects.filter(emitter=user_visited, receiver=user_loged)

		ms = list(mlog)
		for m in mvis:
			if m.visualized == False:
				m.visualized = True
				m.save()
			ms.append(m)

		lista =  sorted(ms, key=lambda inst: inst.date_message)

		json = []

		for msg in lista:
			if msg.emitter == user_loged:
				a = [0, msg.text, self.format_date_chat(msg.date_message)]
			else:
				a = [1, msg.text, self.format_date_chat(msg.date_message)]
			json.append(a)
		return json

	def get_messages_not_view(self, user_loged, user_visited):
		mvis = Message.objects.filter(emitter=user_visited, receiver=user_loged)

		return [(
		    [m.text],
		    [
		        "{}/{} - {}:{}:{}".format(
		            m.date_message.month,
		            m.date_message.day,
		            m.date_message.hour,
		            m.date_message.minute,
		            m.date_message.second,
		        )
		    ],
		) for m in mvis if m.visualized == False]

	def set_read_message(self, user_loged, user_visited):
		mvis = Message.objects.filter(emitter=user_visited, receiver=user_loged)
		for m in mvis:
			if m.visualized == False:
				m.visualized = True
				m.save()
		return True

	def send_message(self, user_loged, user_visited, message_text):
		newMessage = Message()
		newMessage.text = message_text
		newMessage.emitter = user_loged
		newMessage.receiver = user_visited
		newMessage.save()
		return[newMessage.text, self.format_date_chat(newMessage.date_message)]

	def get_ultimate_message(self, user_loged, user_visited):
		mlog = Message.objects.filter(emitter=user_loged, receiver=user_visited)
		mvis = Message.objects.filter(emitter=user_visited, receiver=user_loged)

		ms = list(mlog)
		for m in mvis:ms.append(m)

		if not ms:return False

		return sorted(ms, key=lambda inst: inst.date_message)[-1]

	def check_read_ultimate_message(self, user_loged, user_visited):
		ultimate_message = self.get_ultimate_message(user_loged, user_visited)
		if (ultimate_message != False and ultimate_message.emitter == user_loged
		    and ultimate_message.visualized == True):
			return True
		return False

	def delete_messages(self, user_loged, user_visited):
		Message.objects.filter(emitter=user_loged, receiver=user_visited).delete()
		Message.objects.filter(emitter=user_visited, receiver=user_loged).delete()
		return True
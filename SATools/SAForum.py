from SATools.SAThread import SAThread
from collections import OrderedDict as ordered

import bs4
import re


class SAForum(object):
	def __init__(self, id, session, name=None, subforums=dict(), parent=None):
		self.name = name
		self.id = id
		self.session = session
		self.subforums = subforums
		self.parent = parent

		self.base_url = \
			'http://forums.somethingawful.com/forumdisplay.php'

		self.content = None
		self.listings = None
		self.threads = None
		self.pages = None


	def read(self, pg=1):
		self.threads = self._get_threads(pg)
		self.listings = {threadid: thread.name
		                 for threadid, thread in self.threads.items()}

		if self._has_subforums():
			self.subforums = ordered(self._get_subforums())

	def _has_subforums(self):
		return self.content.table['id'] == 'subforums'

	def _get_subforums(self):
		if not self.subforums:
			for tr_subforum in self.content.select('tr.subforum'):
				subforum_id = tr_subforum.a['href'].split("forumid=")[-1]
				name = tr_subforum.a.text

				forum_obj = SAForum(subforum_id, self.session, name, parent=self)

				yield subforum_id, forum_obj
		return

	def _get_threads(self, pg):
		response = self.session.post(self.base_url,
		                        {'forumid': self.id,
		                         'pagenumber': pg})

		self.content = bs4.BeautifulSoup(response.content)
		threads = ordered(self._gen_threads())

		return threads

	def _gen_threads(self):
		thread_blocks = self.content.select('tr.thread')

		for tr_thread in thread_blocks:
			thread_id = tr_thread['id'][6:]
			properties = self._parse_tr_thread(tr_thread)
			title = properties['title']

			key = thread_id
			val = SAThread(thread_id, self.session, title, **properties)

			yield key, val

	def _parse_tr_thread(self, tr_thread):
		properties = dict()

		for td in tr_thread.find_all('td'):
			td_class = td['class'].pop()
			text = td.text.strip()

			if td_class == 'icon':
				properties[td_class] = td.a['href'].split('posticon=').pop(-1)

			elif td_class == 'lastpost':
				groups = 'time', 'date', 'user'
				regex = "([0-9]+:[0-9]+) ([A-Za-z 0-9]*, 20[0-9]{2})(.*)"

				matches = re.compile(regex).search(text).groups()
				matches = {group: match for group, match in zip(groups, matches)}

				properties[td_class] = matches

			elif td_class == 'replies':
				properties['pages'] = int(int(text) / 40)
				properties[td_class] = text

			elif td_class == 'author':
				user_id = td.a['href'].split('id=')[-1]
				properties['user_id'] = user_id
				properties[td_class] = text

			elif td_class == 'title' or td_class == 'title_sticky':
				link_text = td.find('a','thread_title').text
				properties['title'] = link_text
				properties[td_class] = link_text

			else:
				properties[td_class] = text

		return properties


def main():
	pass


if __name__ == "__main__":
	main()
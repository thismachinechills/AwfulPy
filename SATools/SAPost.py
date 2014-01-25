from SATools.SAPoster import SAPoster


class SAPost(object):
	def __init__(self, id, session, content=None, parent=None):
		self.id = id
		self.content = content
		self.session = session
		self.parent = parent
		self.unread = True
		self.url = ""

		user_id = self.content.td['class'].pop()[7:]
		user_name = self.content.dt.text

		self.poster = SAPoster(user_id,
		                       user_name,
		                       session=self.session,
		                       content=self.content.find('td', 'userinfo'))

		if content:
			self.body = content.td.next_sibling.next_sibling.text.strip()
			self.unread = False

	def read(self):
		self.unread = False
		for td in self.content.find_all('td'):
			if td['class'] == 'userinfo':
				for dd in td.find_all('dd'):
					pass
		raise NotImplemented


def main():
	pass


if __name__ == "__main__":
	main()

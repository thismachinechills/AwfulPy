from SATools.SAForum import SAForum
import bs4
from collections import OrderedDict as ordered

class SAIndex(object):
	def __init__(self, sa_session):
		self.session, self.base_url = sa_session, sa_session.base_url

		self.content = sa_session.get(sa_session.base_url).content
		self.content = bs4.BeautifulSoup(self.content)

		self.listings = self._get_forums_listing()

		self.forums = ((id, SAForum(id, self.session, name=name))
		               for id, name in self.listings.items())
		self.forums = ordered(self.forums)


	def _get_forums_listing(self):
		gen_listings = ((link['href'].split('=')[-1], link.text)
		                for link in self.content.find_all('a')
		                if 'forumid' in link['href'])

		return ordered(gen_listings)





def main():
	pass


if __name__ == "__main__":
	main()
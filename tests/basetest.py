# Base test class
# File named like this to not to match test*.py that test runner is looking for

class TestBase(object):
    def test_title(self):
        """
        Check if there's correct <title> in the page.
        Title format is 'Title | www.my.com'
        """

        # In case of redirect, follow to the redirected page
        response = self.c.get(self.url, follow=True)
        #print self.url
        self.assertRegexpMatches(response.content, '<title>\S+.* \|')

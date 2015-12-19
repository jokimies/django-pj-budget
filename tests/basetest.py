# Base test class
# File named like this to not to match test*.py that test runner is looking for

class BaseTest(object):

    def test_title(self):
        """
        Check if there's correct <title> in the page.
        Title format is 'Title | www.my.com'
        """

        # In case of redirect, follow to the redirected page
        response = self.client.get(self.url, follow=True)
        #print self.url

        # In python3 response.content is 'bytes'
        # https://docs.djangoproject.com/en/1.8/topics/python3/#httprequest-and-httpresponse-objects 
        self.assertRegexpMatches(str(response.content), '<title>\S+.* \|')

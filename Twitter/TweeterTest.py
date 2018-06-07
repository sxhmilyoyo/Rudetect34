import botometer

class TweeterTest():
	"""Test tweeter"""
	def __init__(self):
		self.mashape_key = "huJ4eHqRZtmshEOfjh5vWiOfTKFjp1YKu2ajsngZCjk06Ni4Ok"
		self.twitter_app_auth ={
			'consumer_key': '78FybYOm9mG2YsObvjBHNzMVr',
			'consumer_secret': 'oXIkTt3270uXh1wZioYPMYjRM2A9nazB8OUTfm69YJoeUjHXMm',
			'access_token': '3430332791-gKsOnaa8ZnmCQfyORly3s4F155vrUn5b5FxvV96',
			'access_token_secret': 'oe6UqCEpB4nmgnpYdYVYWWLqNtajObbj1SOJvChPzfnKh'
		}
		self.bom = botometer.Botometer(wait_on_ratelimit=True,
								  mashape_key=self.mashape_key,
								  **self.twitter_app_auth)

	def testTwitter(self, username):
		result = self.bom.check_account(username)
		return result

	def getScore(self, result):
		return result['scores']['english']


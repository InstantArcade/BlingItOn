from random import randrange # random numbers

class EightBall:
    sayings = [
        "I'm Positive (with reference to Ground)",
        'The datasheet says Yes!',
        'Marketing have already sold this as true',
        'Hack, yeah!',
        'Confirmed by passing the test suite',
        "A couple of volts either way can't do any harm",
        'Confident enough for Engineering',
        'Low chance of letting the magic smoke out',
        'My Binary answer is 1',
        "I'm confident of success since the last patch",
        'Response timed out, Retry?',
        '404',
        'Checksum Failed',
        'Out of AI credits.',
        'Read the datasheet then ask a better question',
        "Sorry, it's only good in Development",
        'My Binary answer is 0',
        'It would be like pushing to Production on Friday afternoon',
        'Outlook not so good. And Excel also sucks!',
        'Hack, no!'
        ]
    
    def __init__(self):
        pass
    
    
    def get_random_saying(self):
        num_phrases = len(self.sayings)
        pick = randrange(0,num_phrases)

        return self.sayings[pick]


class MotionModel(object):
    '''Base class for all motion models'''
    
    def model(self, *args, **kwargs):
        '''Override this method to make your own motion model.

        This method should take the time and other optional parameters
        '''
        
        raise Exception('Not implemented')

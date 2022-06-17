from model.masks import MaskInstance

class Player:
    """
    A class that is called by the game being run. This can be automatic, manual, or helped.
    """
    def provide(self) -> str:
        """
        Provide an answer to the game.
        """
        raise NotImplementedError

    def accept(self, *mask: MaskInstance):
        """
        Accept the result
        """
        raise NotImplementedError

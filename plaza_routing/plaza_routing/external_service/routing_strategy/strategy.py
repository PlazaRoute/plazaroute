import abc


class Strategy(metaclass=abc.ABCMeta):

    @abc.abstractmethod
    def route(self, start, destination):
        """
        Returns an array of coordinates for a route defined by
        start and destination.
        Ex. [[8.544978, 47.366343], [8.545068, 47.366354]]
        """
        pass

class ISerializable:
    def serialize(self, action_name: str, payload: dict):
        pass
    @classmethod
    def deserialize(cls, payload: dict):
        """
        Notice the data required is only the `payload`
        """
        pass
        
class Acknowledgement(ISerializable):
    
    
    def serialize(self, action_name: str, payload: dict):
        
        return super().serialize(action_name, payload)
    
    @classmethod
    def deserialize(cls, payload: dict):
        
        return Acknowledgement()
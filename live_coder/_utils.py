

class Stack():
    def __init__(self):
        self.values = []

    def peak(self):
        if not self.values:
            return None
        return self.values[-1]

    def pop(self):
        if not self.values:
            return None
        return self.values.pop(-1)

    def add(self, val):
        self.values.append(val)

    def __len__(self):
        return len(self.values)

    def to_dict(self):
        return {
            'values': [v.to_dict() if type(v) is not list else [vv.to_dict() for vv in v] for v in self.values],
        }

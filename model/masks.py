from typing import List


class Mask:
    convert = '_?X'

    def __init__(self, mask: List[int]):
        self.mask = mask

    def __hash__(self):
        val = 0
        for i in self.mask[::-1]:
            val *= 3
            val += i
        return val

    def __getitem__(self, item):
        return self.mask.__getitem__(item)

    def __eq__(self, other):
        return self.mask == other.mask

    def __repr__(self):
        return "".join(self.convert[i] for i in self.mask)

    def __str__(self):
        return "".join(self.convert[i] for i in self.mask)

    @property
    def solved(self):
        return all(p == 2 for p in self.mask)

    @classmethod
    def for_answer(cls, answer: str, guess: str):
        n = len(answer)
        resp = [0 for i in range(n)]
        bucket = list(answer)
        for i in range(0, n):
            if guess[i] == answer[i]:
                resp[i] = 2
                bucket.remove(answer[i])
        for i in range(0, n):
            if resp[i] < 2 and guess[i] in bucket:
                resp[i] = 1
                bucket.remove(guess[i])
        return Mask(resp)

    @classmethod
    def numbered(cls, p, l=5):
        n: int = int(p)
        def base(val, c):
            while (c > 0):
                yield val % 3
                val //= 3
                c -= 1
        return Mask(list(base(n, l)))


class MaskInstance:
    def __init__(self, mask: Mask, cause: str):
        self.mask = mask
        self.cause = cause

    def matches(self, subject: str):
        available_to_match_anywhere = list(subject)
        for i in range(len(self.cause)):
            # self.cause is trace
            # self.thing is ____X
            sch = subject[i]
            compch = self.cause[i]
            if self.mask[i] == 2:
                # This must match in the same place
                if sch != compch or compch not in available_to_match_anywhere:
                    return False
                available_to_match_anywhere.remove(sch)
            elif self.mask[i] == 1:
                # This must match somewhere, but not here
                if sch == compch or compch not in available_to_match_anywhere:
                    return False
                available_to_match_anywhere.remove(compch)
            elif subject[i] == self.cause[i]:
                return False
        for i in range(len(self.cause)):
            if self.mask[i] == 0:
                if subject[i] == self.cause[i] or self.cause[i] in available_to_match_anywhere:
                    return False
        return True

    def __str__(self):
        base = [Mask.convert[i] for i in self.mask]
        removed = set(self.cause)
        for i, ch in enumerate(self.cause):
            if self.mask[i] == 2:
                base[i] = ch.upper()
                if ch in removed: removed.remove(ch)
            elif self.mask[i] == 1:
                base[i] = ch.lower()
                if ch in removed: removed.remove(ch)

        return "| " + "".join(base) + " |" + \
               ((" Not present: " + removed.__str__()) if removed else "")


    @classmethod
    def for_answer(cls, answer: str, guess: str):
        return MaskInstance(Mask.for_answer(answer, guess), guess)

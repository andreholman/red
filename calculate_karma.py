import pprint
pp = pprint.PrettyPrinter(indent=4,compact=False)

total_karma = [] # calculates total karma from post score (up- minus down-votes)

for i in range(-102, 100000):
    total_karma.append((8270 * i) / (i+8520))

# pp.pprint(total_karma)
additive_karma = []

for i in range(len(total_karma) - 1):
    additive_karma.append(total_karma[i+1] - total_karma[i])

class Post:
    def __init__(self, author, score=0):
        self.author = author
        self.score = score
        
    score = 0
    def upvote(self):
        try:
            self.author.karma += additive_karma[self.score-100]
            self.score += 1
        except: pass
    def downvote(self):
        try:
            self.author.karma -= additive_karma[self.score-101]
            self.score -= 1  
        except: pass

class User:
    def __init__(self, karma=0):
        self.karma = karma
    
qi = User(karma=0)

p = Post(author=qi, score=0)

with open('additive_karma.txt','w') as file:
    for decimal in additive_karma:
	    file.write(str(decimal) + ", ")
            
with open("additive_karma.txt") as file:
    read_values = file.read().split(',')

print(read_values[102])
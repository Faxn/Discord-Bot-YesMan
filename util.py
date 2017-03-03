import os

async def get_messages(client, channel, before=None):
    payload = {'limit':100}
    if before:
        payload["before"] = before
    
    url = '{0.CHANNELS}/{1}/messages'.format(client.http, channel.id)
    messages = await client.http.get( url, params=payload )
    return messages
    
async def get_all_messages(client, channel):
    messages = await get_messages(client, channel)
    
    last_snowflake = messages[-1]['id']
    while True:
        print("getting messages before %r" % (last_snowflake))
        new_messages = await get_messages(client, channel, last_snowflake)
        if len(new_messages) == 0:
            break
        messages.extend(new_messages)
        last_snowflake=new_messages[-1]['id']
    
    with open(get_storage(channel), 'w') as outfile:
        import json
        outfile.write(json.dumps(messages))
        
    return messages
        

def get_storage(channel):
    os.makedirs("data/channels/", exist_ok=True)
    return "data/channels/%s-%s.json" % (channel.id, channel.name )
    

import json
def build_corpus(userid):
    corpus = []
    for fname in os.listdir("data/channels/"):
        with open("data/channels/"+fname) as fp:
           messages = json.load(fp)
        for m in messages:
            if (m["author"]["id"] == userid):
                corpus.append(m["content"])
           
    with open("corpus-%s.json"%(userid), 'w') as fp:
        json.dump( corpus, fp)

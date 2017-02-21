

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
    return messages
        


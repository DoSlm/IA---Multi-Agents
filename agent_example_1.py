from spade import agent, quit_spade

class DummyAgent(agent.Agent):
    async def setup(self):
        print("Hello World! I'm agent {}".format(str(self.jid)))

dummy = DummyAgent("your_jid@your_xmpp_server", "your_password")
future = dummy.start()
future.result()

dummy.stop()
quit_spade()
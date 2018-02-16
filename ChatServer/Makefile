
JFLAGS = -d bin -sourcepath src
JC = javac
.SUFFIXES: .java .class
.java.class:
	$(JC) $(JFLAGS) $*.java

CLASSES = \
	src/Model/Client.java \
	src/Model/MessageBundle.java \
	src/Model/Message.java \
	src/UI/ChatAppUI.java \
	src/RunClient.java \
	src/RunServer.java \
	src/Controller/ClientUI.java \
	src/Controller/ClientInterface.java \
	src/Controller/ClientCLI.java \
	src/Service/Server.java \
	src/Service/ClientImpl.java \
	src/Service/ServerImpl.java \
	src/Service/Client.java

default: classes

classes: $(CLASSES:.java=.class)

clean:
	rm -r bin/*

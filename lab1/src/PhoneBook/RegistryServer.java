package registry;
/*
 * Copyright (c) 2013, Oracle and/or its affiliates. All rights reserved.
 *
 * Redistribution and use in source and binary forms, with or without
 * modification, are permitted provided that the following conditions
 * are met:
 *
 *   - Redistributions of source code must retain the above copyright
 *     notice, this list of conditions and the following disclaimer.
 *
 *   - Redistributions in binary form must reproduce the above copyright
 *     notice, this list of conditions and the following disclaimer in the
 *     documentation and/or other materials provided with the distribution.
 *
 *   - Neither the name of Oracle or the names of its
 *     contributors may be used to endorse or promote products derived
 *     from this software without specific prior written permission.
 *
 * THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS
 * IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO,
 * THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR
 * PURPOSE ARE DISCLAIMED.  IN NO EVENT SHALL THE COPYRIGHT OWNER OR
 * CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL,
 * EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO,
 * PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR
 * PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF
 * LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING
 * NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
 * SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
 */

import java.net.*;
import java.io.*;
import java.util.*;

import registry.*;

public class RegistryServer {
    public static void main(String[] argv) throws IOException {

        if (argv.length != 1) {
            System.err.println("Usage: java EchoServer <port number>");
            System.exit(1);
        }

        HashMap<String, Person> registry = new HashMap<>();

        int portNumber = Integer.parseInt(argv[0]);

        try (
            ServerSocket serverSocket =
                new ServerSocket(portNumber);

            Socket clientSocket = serverSocket.accept();

            ObjectOutputStream out =
              new ObjectOutputStream(clientSocket.getOutputStream());

            ObjectInputStream in =
                new ObjectInputStream(clientSocket.getInputStream());
        ) {
            out.flush();
            
            Command command;
            while ((command = (Command)in.readObject()) != null) {
              ArrayList<Object> args = new ArrayList<>();
              switch (command.action()){
                case ADD:
                  Person p = (Person)command.objectAt(0);
                  if (registry.containsKey(p.fullname)){
                    System.out.println("Cannot add "+p.fullname+": it already exists");

                    args.add(p.fullname+" already exists");
                    out.writeObject(new Command(Command.Type.FAIL, args));
                    break;
                  }
                  registry.put(p.fullname, p);
                  out.writeObject(new Command(Command.Type.SUCCESS));
                  break;
                case GET:
                  String fullname = (String)command.objectAt(0);
                  if (!registry.containsKey(fullname)){
                    System.out.println("Cannot get "+fullname+": it doesn't exists");

                    args.add(fullname+" doesn't exists");
                    out.writeObject(new Command(Command.Type.FAIL, args));
                    break;
                  }

                  args.add(registry.get(fullname));
                  out.writeObject(new Command(Command.Type.SUCCESS, args));
                  break;
                case LIST:
                  for (Map.Entry<String, Person> o: registry.entrySet())
                    args.add(o.getValue());
                  out.writeObject(new Command(Command.Type.SUCCESS, args));
                  break;
                default:
                  System.out.println("Unknow action");
                  break;
              }
            }
            System.out.println("I'm ending...");
        } catch (IOException e) {
            System.out.println("Exception caught when trying to listen on port "
                + portNumber + " or listening for a connection");
            System.out.println(e.getMessage());
        } catch(ClassNotFoundException e){
          System.out.println("Unknow object received");
        }
    }
}

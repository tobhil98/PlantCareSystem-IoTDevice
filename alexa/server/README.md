# Server Configuration

The following steps are done automatically when the server is booted. 

## Common Gateway Interface

The CGI script must be placed in `/home/cgi-bin` and the CGI capable HTTP request handler must be started one directory below in `/home`.

Starting the handler:


```
python -m CGIHTTPServer 8000
```

POST data sent by the skill (AWS) is put on `stdin` in a JSON-format. All replies to the skill must be put on `stdout` following the `Request and Response JSON Reference` provided by amazon. 
At least a version number (string) and a response are to be provided (response object).

The JSON mesasge posted to `stdin` is not terminated by a new line or EOF. `stdin` is therefore read one byte at a time checkng for balanced brackets in order to obtain the full message.

## Ngrok

Ngrok is used to relay data when the HTTP POST and GET methods are used. It provides a public address which AWS uses to send a query to our server. 

Information is relayed first to the Ngrok service running locally and then to the CGI HTTP handler using the specified port (8000).

The Ngrok tunnel is started by executing the following command in the home directory.

```
./ngrok HTTP 8000
```

## Database Access

The server queries and updates the database to fulfill and answer requests from alexa. 
The procedure is the same as the one used in [proxy](../../proxy)



## References

Request and Response JSON Reference:

https://developer.amazon.com/en-GB/docs/alexa/custom-skills/request-and-response-json-reference.html#response-format

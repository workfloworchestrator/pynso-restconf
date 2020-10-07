Getting started
~~~~~~~~~~~~~~~

In order to enable RESTCONF in NSO, RESTCONF must be enabled in the ncs.conf configuration
file. The web server configuration for RESTCONF is shared with the WebUI's config. However, the
WebUI does not have to be enabled for RESTCONF to work.

Here's a minimal example of what is needed in the ncs.conf file:

.. sourcecode:: xml

    <restconf>
        <enabled>true</enabled>
    </restconf>
    <webui>
        <enabled>false</enabled>
        <transport>
            <tcp>
                <enabled>true</enabled>
                <ip>0.0.0.0</ip>
                <port>8080</port>
            </tcp>
        </transport>
    </webui>
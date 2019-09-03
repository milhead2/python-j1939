python-j1939
==========

Society of Automotive Engineers standard SAE J1939 is the vehicle bus 
recommended practice used for communication and diagnostics among vehicle 
components. Originating in the car and heavy-duty truck industry in the 
United States, it is now widely used in other parts of the world.

SAE J1939 is used in the commercial vehicle area for communication throughout 
the vehicle, with the physical layer defined in ISO 11898. A different 
physical layer is used between the tractor and trailer, specified in ISO 11992. 

This package is dependent on, was a part of, and broken out from,  the `python-can <https://github.com/hardbyte/python-can/>`__ project that Brian Thorne has maintained for years..

This codce currently is compatable with the python-can version 3.3.2.  After you clone the python-can repo be sure to checkout the 'release-3.3.2' branch

The **C**\ ontroller **A**\ rea **N**\ etwork is a bus standard designed
to allow microcontrollers and devices to communicate with each other. It
has priority based bus arbitration, reliable deterministic
communication. It is used in cars, trucks, boats, wheelchairs and more.

The ``can`` package provides controller area network support for
Python developers; providing `common abstractions to
different hardware devices`, and a suite of utilities for sending and receiving
messages on a can bus.

In all of my code that used the former protocol import from python-can I 
needed only to make a small change.  Generally a shortning of the import 
statements..  For example

    from can.protocols import j1939

becomes

    import j1939



The library (should) support Python 2.7, Python 3.3+ and run on Mac, Linux and Windows; however, at this early time I am only testing on Python 3.4.0 on Linux 3.16.0-38-generic #52~14.04.1-Ubuntu SMP Fri May 8 09:43:57 UTC 2015 x86_64 x86_64 x86_64 GNU/Linux


Discussion
----------

If you run into bugs, you can file them in 
`issue tracker <https://github.com/milhead2/python-j1939/issues>`__.
(Any help is appriciated!)

Wherever we interact, we strive to follow the
`Python Community Code of Conduct <https://www.python.org/psf/codeofconduct/>`__.

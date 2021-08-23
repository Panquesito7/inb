# Chromedriver Service

This serivce provides a webdriver instance for our application to use. We can also provide _Chromedriver_ `options` while
instantiating a _chromedriver_ object.

This document has the following sections:

- [Driver Overview](#driver-overview)
- [Driver Options](#driver-options)
- [System Call Interface](#system-call-interface)

## Driver Overview

**Driver Class:**

> Class `Driver` has a base class `object` which is the default base class of all the classes in python, so there is nothing much in
> that. <br><br>
> `class Driver(object):`

**Driver Constructor:**

> The constructor method takes in some arguments, one is compulsory and the other one is optional. <br><br>
> `def __init__(self: Driver, driver_path: str, options: list = []) -> None:` <br><br>
> Argument `driver_path` is neccessary to locate the chromedriver executable in your system, you must give the absolute path to the `chromedriver` executable in your system. <br>
> Argument `options` is optional, it is a list of chromedriver options that you may want to enable while automating the browser. <br>

**Driver Destructor:**

> The destructor method turns the `Driver` class variable `__SESSION_ALREADY_EXISTS` to `False` which was set to `True` when you instantiate a `chromedriver` object. <br><br>
> `def __del__(self: Driver) -> None:` <br><br>
> It also calls the `quit` method (not `close` method) on the `chromedriver` object to delete the `chromedriver` instance. 

## Driver Options

> `HEADLESS: str = "--headless"` (Sets the `chromedriver` in `headless` mode.) <br>
> `INCOGNITO: str = "--incognito"` (Sets the `chromedriver` in `incognito` mode.) <br>
> `NO_SANDBOX: str = "--no-sandbox"` (Sets the `chromedriver` in `no-sandbox` mode.) <br>
> `DISABLE_GPU: str = "--disable-gpu"` (Sets the `chromedriver` in `disable-gpu` mode.) <br>
> `START_MAXIMIZED: str = "--start-maximized"` (Sets the `chromedriver` in `start-maximized` mode.) <br>
> `DISABLE_INFOBARS: str = "--disable-infobars"` (Sets the `chromedriver` in `disable-inforbars` mode.) <br>
> `ENABLE_AUTOMATION: str = "--enable-automation"` (Sets the `chromedriver` in `enable-automation` mode.) <br>
> `DISABLE_EXTENSIONS: str = "--disable-extensions"` (Sets the `chromedriver` in `disable-extensions` mode.) <br>
> `DISABLE_NOTIFICATIONS: str = "--disable-notifications"` (Sets the `chromedriver` in `disable-notifications` mode.) <br>
> `DISABLE_SETUID_SANDBOX: str = "--disable-setuid-sandbox"` (Sets the `chromedriver` in `disable-setuid-sandbox` mode.) <br>
> `IGNORE_CERTIFICATE_ERRORS: str = "--ignore-certificate-errors"` (Sets the `chromedriver` in `ignore-certificate-errors` mode.) <br>

## System Call Interface

**Method enable_webdriver_chrome()**

> This method enables the `chromedriver` instance in the `Driver` instance. <br><br>
> `def enable_webdriver_chrome(self: Driver) -> None:` <br><br>
> This is the actual method that adds a `chromedriver` instance to the `Driver` instance, without calling this method the `Driver` instance will not have a `chromedriver` object. <br>

**Method disable_webdriver_chrome()**

> This method disables the `chromedriver` instance in the `Driver` instance by calling the `quit` (not `close`) method on it. <br><br>
> `def disable_webdriver_chrome(self: Driver) -> None:` <br><br>
> This method also sets the class variable `__SESSION_ALREADY_EXISTS` to `False`, in simple words this method is identical to the _destructor_ method.
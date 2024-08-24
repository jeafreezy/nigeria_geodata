"""
Enum definitions for nigeria_geodata.

This module contains enumerations used throughout the nigeria_geodata package. It includes
enumerations for HTTP request methods and Nigerian states.

Enums:
    - RequestMethod: Defines HTTP request methods (GET, POST).
    - NigeriaState: Defines all states in Nigeria, including the Federal Capital Territory (FCT).

Usage:
    These enums are used to standardize certain constant values such as HTTP methods
    and state names throughout the package.

Example:
    - RequestMethod.GET
    - NigeriaState.LAGOS
"""

from enum import Enum


class RequestMethod(Enum):
    """
    Enumeration for HTTP request methods.

    This class defines common HTTP request methods used for making network requests.
    """

    GET = "GET"
    """HTTP GET request method"""
    POST = "POST"
    """HTTP POST request method"""


class NigeriaState(Enum):
    """
    Enumeration for Nigerian states and the Federal Capital Territory (FCT).

    This class defines all the states and the Federal Capital Territory (FCT) in Nigeria.
    Each value corresponds to the official name of the state or territory.
    """

    ABIA = "Abia"
    ADAMAWA = "Adamawa"
    AKWA_IBOM = "Akwa Ibom"
    ANAMBRA = "Anambra"
    BAUCHI = "Bauchi"
    BAYELSA = "Bayelsa"
    BENUE = "Benue"
    BORNO = "Borno"
    CROSS_RIVER = "Cross River"
    DELTA = "Delta"
    EBONYI = "Ebonyi"
    EDO = "Edo"
    EKITI = "Ekiti"
    ENUGU = "Enugu"
    GOMBE = "Gombe"
    IMO = "Imo"
    JIGAWA = "Jigawa"
    KADUNA = "Kaduna"
    KANO = "Kano"
    KATSINA = "Katsina"
    KEBBI = "Kebbi"
    KOGI = "Kogi"
    KWARA = "Kwara"
    LAGOS = "Lagos"
    NASARAWA = "Nasarawa"
    NIGER = "Niger"
    OGUN = "Ogun"
    ONDO = "Ondo"
    OSUN = "Osun"
    OYO = "Oyo"
    PLATEAU = "Plateau"
    RIVERS = "Rivers"
    SOKOTO = "Sokoto"
    TARABA = "Taraba"
    YOBE = "Yobe"
    ZAMFARA = "Zamfara"
    FCT = "Abuja"  # Abuja is the name used in the data, but the user must provide FCT

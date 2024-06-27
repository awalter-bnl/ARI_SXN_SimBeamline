from caproto import ChannelType
from caproto.server import pvproperty, ioc_arg_parser, run, PVGroup
from textwrap import dedent


class TwoButtonShutter(PVGroup):
    """
    A PVGroup that simulates the action of an NSLS-II TwoButtonShutter device.

    A PVGroup that simulates the standard IOC for an NSLS-II TwoButtonShutter
    device, which includes photon shutters, pneumatic gate-valves and
    angle-valves
    """

    # Shutter properties
    open_cmd = pvproperty(name=':Cmd:Opn-Cmd', dtype=ChannelType.ENUM,
                          value='idle', enum_strings=['idle', 'Open'])
    close_cmd = pvproperty(name=':Cmd:Cls-Cmd', dtype=ChannelType.ENUM,
                           value='idle', enum_strings=['idle', 'Close'])
    status = pvproperty(name=':Pos-Sts', value='Open', read_only=True,
                        report_as_string=True)


# Add some code to start a version of the server if this file is 'run'.
if __name__ == "__main__":
    ioc_options, run_options = ioc_arg_parser(
        default_prefix="TwoButtonShutter",
        desc=dedent(TwoButtonShutter.__doc__))
    ioc = TwoButtonShutter(**ioc_options)
    run(ioc.pvdb, **run_options)

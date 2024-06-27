from caproto import ChannelType
from caproto.server import pvproperty, ioc_arg_parser, run, PVGroup
from textwrap import dedent


class TwoButtonShutter(PVGroup):
    """
    A PVGroup that simulates the action of an NSLS-II TwoButtonShutter device.

    A PVGroup that simulates the standard IOC for an NSLS-II TwoButtonShutter
    device, which includes photon shutters, pneumatic gate-valves and
    angle-valves.

    NOTES:
    1. Unless otherwise listed in the notes below the PVs generated are 'Dummy'
    PVs that are not modified by any inputs, or modify any other PVs, except
    there own values when they are updated.
    2. When self.open_cmd/close_cmd is set to 'Open'/'Close', or 1/1 the
    sequence of events is:
        i. If self.status is equal to 'Open'/'Not Open' then set self.open_cmd/
        self.close_cmd to 'idle' or 0.
        ii. Else wait XX seconds then set self.status to 'Open'/'Not Open'

    """

    # Shutter properties
    open_cmd = pvproperty(name=':Cmd:Opn-Cmd', dtype=ChannelType.ENUM,
                          value='idle', enum_strings=['idle', 'Open'])
    close_cmd = pvproperty(name=':Cmd:Cls-Cmd', dtype=ChannelType.ENUM,
                           value='idle', enum_strings=['idle', 'Close'])
    status = pvproperty(name=':Pos-Sts', value='Open', read_only=True,
                        report_as_string=True)
    fail_to_close = pvproperty(name=':Sts:FailCls-Sts', value='False',
                               read_only=True, report_as_string=True)
    fail_to_open = pvproperty(name=':Sts:FailOpn-Sts', value='False',
                              read_only=True, report_as_string=True)
    enable_status = pvproperty(name=':Enbl-Sts', value='True',
                               read_only=True, report_as_string=True)


# Add some code to start a version of the server if this file is 'run'.
if __name__ == "__main__":
    ioc_options, run_options = ioc_arg_parser(
        default_prefix="TwoButtonShutter",
        desc=dedent(TwoButtonShutter.__doc__))
    ioc = TwoButtonShutter(**ioc_options)
    run(ioc.pvdb, **run_options)

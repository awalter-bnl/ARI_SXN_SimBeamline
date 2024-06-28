from caproto import ChannelType
from caproto.server import pvproperty, ioc_arg_parser, run, PVGroup
from textwrap import dedent
import time


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
        self.close_cmd to 'Idle' or 0.
        ii. Else wait XX seconds then set self.status to 'Open'/'Not Open'

    """

    def __init__(self, *args, actuation_time=1.5, **kwargs):
        """
        An init function that sets an attribute called _activation_time.

        This performs the parent initialization and then adds abn attribute for
        activation time that can be set during instantiation.

        Parameters
        ----------
        *args :
            Arguments passed to the parent class __init__ method
        actuation_time_time :
            The time (in seconds) that the device should take to actuate
        **kwargs :
           Keyword arguments passed to the parent class __init__ method
        """
        super().__init__(*args, **kwargs)
        self._actuation_time = actuation_time

    # Shutter properties
    open_cmd = pvproperty(name=':Cmd:Opn-Cmd', dtype=ChannelType.ENUM,
                          value='Idle', enum_strings=['Idle', 'Open'])
    close_cmd = pvproperty(name=':Cmd:Cls-Cmd', dtype=ChannelType.ENUM,
                           value='Idle', enum_strings=['Idle', 'Close'])
    status = pvproperty(name=':Pos-Sts', value='Open', read_only=True,
                        report_as_string=True)
    fail_to_close = pvproperty(name=':Sts:FailCls-Sts', value='False',
                               read_only=True, report_as_string=True)
    fail_to_open = pvproperty(name=':Sts:FailOpn-Sts', value='False',
                              read_only=True, report_as_string=True)
    enable_status = pvproperty(name=':Enbl-Sts', value='True',
                               read_only=True, report_as_string=True)

    # noinspection PyMethodParameters
    @open_cmd.putter
    async def open_cmd(obj, instance, value):
        """
        This is a putter function that steps through the proces required when
        the 'open_cmd' PV is set to 'Open'. If it is set to 'Not Open' it just
        sets itself to 'Idle'.
        """
        if value == 'Open':
            await instance.write('Open', verify_value=False)
            start_timestamp = time.time()  # record initial time
            while time.time() - start_timestamp < obj._actuation_time:
                time.sleep(1E-3)
            await obj.status.write('Open')

        return 'Idle'

    # noinspection PyMethodParameters
    @close_cmd.putter
    async def close_cmd(obj, instance, value):
        """
        This is a putter function that steps through the proces required when
        the 'open_cmd' PV is set to 'Open'. If it is set to 'Not Open' it just
        sets itself to 'Idle'.
        """
        if value == 'Close':
            await instance.write('Close', verify_value=False)
            start_timestamp = time.time()  # record initial time
            while time.time() - start_timestamp < obj._actuation_time:
                time.sleep(1E-3)
            await obj.status.write('Not Open')
        return 'Idle'


# Add some code to start a version of the server if this file is 'run'.
if __name__ == "__main__":
    ioc_options, run_options = ioc_arg_parser(
        default_prefix="TwoButtonShutter",
        desc=dedent(TwoButtonShutter.__doc__))
    ioc = TwoButtonShutter(**ioc_options)
    run(ioc.pvdb, **run_options)

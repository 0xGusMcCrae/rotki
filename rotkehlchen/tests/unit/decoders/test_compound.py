import pytest

from rotkehlchen.accounting.structures.balance import Balance
from rotkehlchen.accounting.structures.base import (
    HistoryBaseEntry,
    HistoryEventSubType,
    HistoryEventType,
)
from rotkehlchen.chain.ethereum.modules.compound.constants import CPT_COMPOUND
from rotkehlchen.constants.assets import A_CETH, A_ETH
from rotkehlchen.constants.misc import ZERO
from rotkehlchen.fval import FVal
from rotkehlchen.tests.utils.ethereum import get_decoded_events_of_transaction
from rotkehlchen.types import Location, deserialize_evm_tx_hash

ADDY = '0x5727c0481b90a129554395937612d8b9301D6c7b'


@pytest.mark.parametrize('ethereum_accounts', [[ADDY]])  # noqa: E501
def test_compound_ether_withdraw(database, ethereum_manager, function_scope_messages_aggregator):
    """Data taken from:
    https://etherscan.io/tx/0x024bd402420c3ba2f95b875f55ce2a762338d2a14dac4887b78174254c9ab807
    """
    # TODO: For faster tests hard-code the transaction and the logs here so no remote query needed
    tx_hash = deserialize_evm_tx_hash('0x024bd402420c3ba2f95b875f55ce2a762338d2a14dac4887b78174254c9ab807')  # noqa: E501
    events = get_decoded_events_of_transaction(
        ethereum_manager=ethereum_manager,
        database=database,
        msg_aggregator=function_scope_messages_aggregator,
        tx_hash=tx_hash,
    )
    expected_events = [
        HistoryBaseEntry(
            event_identifier=tx_hash.hex(),  # pylint: disable=no-member
            sequence_index=0,
            timestamp=1598813490000,
            location=Location.BLOCKCHAIN,
            event_type=HistoryEventType.SPEND,
            event_subtype=HistoryEventSubType.FEE,
            asset=A_ETH,
            balance=Balance(amount=FVal('0.02858544'), usd_value=ZERO),
            location_label=ADDY,
            notes=f'Burned 0.02858544 ETH in gas from {ADDY}',
            counterparty='gas',
        ), HistoryBaseEntry(
            event_identifier=tx_hash.hex(),  # pylint: disable=no-member
            sequence_index=1,
            timestamp=1598813490000,
            location=Location.BLOCKCHAIN,
            event_type=HistoryEventType.SPEND,
            event_subtype=HistoryEventSubType.RETURN_WRAPPED,
            asset=A_CETH,
            balance=Balance(amount=FVal('24.97649991'), usd_value=ZERO),
            location_label=ADDY,
            notes='Return 24.97649991 cETH to compound',
            counterparty=CPT_COMPOUND,
        ), HistoryBaseEntry(
            event_identifier=tx_hash.hex(),  # pylint: disable=no-member
            sequence_index=50,
            timestamp=1598813490000,
            location=Location.BLOCKCHAIN,
            event_type=HistoryEventType.WITHDRAWAL,
            event_subtype=HistoryEventSubType.REMOVE_ASSET,
            asset=A_ETH,
            balance=Balance(amount=FVal('0.500003923413507454'), usd_value=ZERO),
            location_label=ADDY,
            notes='Withdraw 0.500003923413507454 ETH from compound',
            counterparty=CPT_COMPOUND,
        )]
    assert events == expected_events

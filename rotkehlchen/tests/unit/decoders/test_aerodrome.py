import pytest

from rotkehlchen.accounting.structures.balance import Balance
from rotkehlchen.accounting.structures.evm_event import EvmEvent, EvmProduct
from rotkehlchen.accounting.structures.types import HistoryEventSubType, HistoryEventType
from rotkehlchen.assets.asset import Asset, EvmToken
from rotkehlchen.assets.utils import get_or_create_evm_token
from rotkehlchen.chain.base.modules.aerodrome.aerodrome_cache import (
    query_aerodrome_data,
    save_aerodrome_data_to_cache,
)
from rotkehlchen.chain.base.modules.aerodrome.constants import CPT_AERODROME
from rotkehlchen.chain.base.modules.aerodrome.decoder import ROUTER
from rotkehlchen.chain.evm.constants import ZERO_ADDRESS
from rotkehlchen.chain.evm.decoding.constants import CPT_GAS
from rotkehlchen.chain.evm.types import string_to_evm_address
from rotkehlchen.constants import ZERO
from rotkehlchen.constants.assets import A_ETH, A_USDBC, A_USDC_BASE, A_WETH_BASE
from rotkehlchen.constants.resolver import evm_address_to_identifier
from rotkehlchen.fval import FVal
from rotkehlchen.tests.utils.ethereum import get_decoded_events_of_transaction
from rotkehlchen.types import (
    AERODROME_POOL_PROTOCOL,
    CacheType,
    ChainID,
    EvmTokenKind,
    Location,
    TimestampMS,
    deserialize_evm_tx_hash,
)

WETH_USDBC_POOL_ADDRESS = string_to_evm_address('0xB4885Bc63399BF5518b994c1d0C153334Ee579D0')
USDC_USDBC_POOL_ADDRESS = string_to_evm_address('0x27a8Afa3Bd49406e48a074350fB7b2020c43B2bD')
AERO_WUSDR_POOL_ADDRESS = string_to_evm_address('0x03e2730cB3FC37315D4DD68d1DcB47358826D291')
WETH_USDBC_GAUGE_ADDRESS = string_to_evm_address('0xeca7Ff920E7162334634c721133F3183B83B0323')
WETH_USDBC_LP_TOKEN = evm_address_to_identifier(
    address=WETH_USDBC_POOL_ADDRESS,
    chain_id=ChainID.BASE,
    token_type=EvmTokenKind.ERC20,
)
AERO_TOKEN = evm_address_to_identifier(
    address=string_to_evm_address('0x940181a94A35A4569E4529A3CDfB74e38FD98631'),
    chain_id=ChainID.BASE,
    token_type=EvmTokenKind.ERC20,
)
AERO_WUSDR_LP_TOKEN = evm_address_to_identifier(
    address=string_to_evm_address('0x03e2730cB3FC37315D4DD68d1DcB47358826D291'),
    chain_id=ChainID.BASE,
    token_type=EvmTokenKind.ERC20,
)


@pytest.mark.vcr()
@pytest.mark.parametrize('base_accounts', [['0x15718b9B0DAdE1C17d8329A13bB9553f3B38e172']])
def test_add_liquidity(base_transaction_decoder, base_accounts):
    """Check that adding liquidity to an aerodrome pool is properly decoded."""
    evmhash = deserialize_evm_tx_hash('0x3ff13e2fefc1bf92ff9bf237e44317328ef7ad21a0a454ed8f9db48d09ff3949')  # noqa: E501
    user_address = base_accounts[0]
    events, _ = get_decoded_events_of_transaction(
        evm_inquirer=base_transaction_decoder.evm_inquirer,
        database=base_transaction_decoder.database,
        tx_hash=evmhash,
    )
    timestamp = TimestampMS(1696541085000)
    expected_events = [
        EvmEvent(
            tx_hash=evmhash,
            sequence_index=0,
            timestamp=timestamp,
            location=Location.BASE,
            event_type=HistoryEventType.SPEND,
            event_subtype=HistoryEventSubType.FEE,
            asset=A_ETH,
            balance=Balance(FVal('0.000017931820152208')),
            location_label=user_address,
            counterparty=CPT_GAS,
            notes='Burned 0.000017931820152208 ETH for gas',
        ), EvmEvent(
            tx_hash=evmhash,
            sequence_index=1,
            timestamp=timestamp,
            location=Location.BASE,
            event_type=HistoryEventType.SPEND,
            event_subtype=HistoryEventSubType.NONE,
            asset=A_ETH,
            balance=Balance(FVal('0.0001')),
            location_label=user_address,
            counterparty=None,
            address=ROUTER,
            product=None,
            notes=f'Send 0.0001 ETH to {ROUTER}',
        ), EvmEvent(
            tx_hash=evmhash,
            sequence_index=6,
            timestamp=timestamp,
            location=Location.BASE,
            event_type=HistoryEventType.INFORMATIONAL,
            event_subtype=HistoryEventSubType.APPROVE,
            asset=A_USDBC.resolve_to_asset_with_symbol(),
            balance=Balance(FVal(0.000002)),
            location_label=user_address,
            counterparty=None,
            address=ROUTER,
            notes=f'Set USDbC spending approval of {user_address} by {ROUTER} to 0.000002',
        ), EvmEvent(
            tx_hash=evmhash,
            sequence_index=7,
            timestamp=timestamp,
            location=Location.BASE,
            event_type=HistoryEventType.DEPOSIT,
            event_subtype=HistoryEventSubType.DEPOSIT_ASSET,
            asset=A_USDBC.resolve_to_asset_with_symbol(),
            balance=Balance(FVal(0.16186)),
            location_label=user_address,
            counterparty=CPT_AERODROME,
            address=WETH_USDBC_POOL_ADDRESS,
            product=EvmProduct.POOL,
            notes=f'Deposit 0.16186 USDbC in aerodrome pool {WETH_USDBC_POOL_ADDRESS}',
        ), EvmEvent(
            tx_hash=evmhash,
            sequence_index=10,
            timestamp=timestamp,
            location=Location.BASE,
            event_type=HistoryEventType.RECEIVE,
            event_subtype=HistoryEventSubType.RECEIVE_WRAPPED,
            asset=Asset(WETH_USDBC_LP_TOKEN).resolve_to_asset_with_symbol(),
            balance=Balance(FVal('0.000000004023175857')),
            location_label=user_address,
            counterparty=CPT_AERODROME,
            address=ZERO_ADDRESS,
            product=EvmProduct.POOL,
            notes=f'Receive 0.000000004023175857 vAMM-WETH/USDbC after depositing in aerodrome pool {WETH_USDBC_POOL_ADDRESS}',  # noqa: E501
        ),
    ]
    assert events == expected_events
    assert EvmToken(WETH_USDBC_LP_TOKEN).protocol == AERODROME_POOL_PROTOCOL


@pytest.mark.vcr()
@pytest.mark.parametrize('base_accounts', [['0x15718b9B0DAdE1C17d8329A13bB9553f3B38e172']])
def test_remove_liquidity(base_inquirer, base_transaction_decoder, base_accounts):
    base_inquirer.ensure_cache_data_is_updated(
        cache_type=CacheType.AERODROME_POOL_ADDRESS,
        query_method=query_aerodrome_data,
        save_method=save_aerodrome_data_to_cache,
    )  # populates cache, addressbook and assets tables
    """Check that removing liquidity from a aerodrome pool is properly decoded."""
    get_or_create_evm_token(  # the token is needed for the approval event to be created
        userdb=base_transaction_decoder.evm_inquirer.database,
        evm_address=string_to_evm_address('0xB4885Bc63399BF5518b994c1d0C153334Ee579D0'),
        chain_id=ChainID.BASE,
        protocol=AERODROME_POOL_PROTOCOL,
        symbol='vAMM-WETH/USDbC',
    )
    evmhash = deserialize_evm_tx_hash('0x62a4f51bec58ea96ec6f70374f195acbba0c42facf392a30a4d99271d193f5bd')  # noqa: E501
    user_address = base_accounts[0]
    events, _ = get_decoded_events_of_transaction(
        evm_inquirer=base_transaction_decoder.evm_inquirer,
        database=base_transaction_decoder.database,
        tx_hash=evmhash,
    )
    timestamp = TimestampMS(1696615179000)
    expected_events = [
        EvmEvent(
            tx_hash=evmhash,
            sequence_index=0,
            timestamp=timestamp,
            location=Location.BASE,
            event_type=HistoryEventType.SPEND,
            event_subtype=HistoryEventSubType.FEE,
            asset=A_ETH,
            balance=Balance(FVal('0.000022300414144718')),
            location_label=user_address,
            counterparty=CPT_GAS,
            notes='Burned 0.000022300414144718 ETH for gas',
        ), EvmEvent(
            tx_hash=evmhash,
            sequence_index=423,
            timestamp=timestamp,
            location=Location.BASE,
            event_type=HistoryEventType.INFORMATIONAL,
            event_subtype=HistoryEventSubType.APPROVE,
            asset=Asset(WETH_USDBC_LP_TOKEN),
            balance=Balance(ZERO),
            location_label=user_address,
            address=ROUTER,
            notes=f'Revoke vAMM-WETH/USDbC spending approval of {user_address} by {ROUTER}',
        ), EvmEvent(
            tx_hash=evmhash,
            sequence_index=424,
            timestamp=timestamp,
            location=Location.BASE,
            event_type=HistoryEventType.SPEND,
            event_subtype=HistoryEventSubType.RETURN_WRAPPED,
            asset=Asset(WETH_USDBC_LP_TOKEN),
            balance=Balance(FVal('0.000000004023175857')),
            location_label=user_address,
            counterparty=CPT_AERODROME,
            address=WETH_USDBC_POOL_ADDRESS,
            product=EvmProduct.POOL,
            notes='Return 0.000000004023175857 vAMM-WETH/USDbC',
        ), EvmEvent(
            tx_hash=evmhash,
            sequence_index=426,
            timestamp=timestamp,
            location=Location.BASE,
            event_type=HistoryEventType.WITHDRAWAL,
            event_subtype=HistoryEventSubType.REMOVE_ASSET,
            asset=A_WETH_BASE,
            balance=Balance(FVal('0.000099213494388347')),
            location_label=user_address,
            counterparty=CPT_AERODROME,
            address=WETH_USDBC_POOL_ADDRESS,
            product=EvmProduct.POOL,
            notes=f'Remove 0.000099213494388347 WETH from aerodrome pool {WETH_USDBC_POOL_ADDRESS}',  # noqa: E501
        ), EvmEvent(
            tx_hash=evmhash,
            sequence_index=427,
            timestamp=timestamp,
            location=Location.BASE,
            event_type=HistoryEventType.WITHDRAWAL,
            event_subtype=HistoryEventSubType.REMOVE_ASSET,
            asset=A_USDBC,
            balance=Balance(FVal('0.163143')),
            location_label=user_address,
            counterparty=CPT_AERODROME,
            address=WETH_USDBC_POOL_ADDRESS,
            product=EvmProduct.POOL,
            notes=f'Remove 0.163143 USDbC from aerodrome pool {WETH_USDBC_POOL_ADDRESS}',
        ),
    ]
    assert events == expected_events


@pytest.mark.vcr()
@pytest.mark.parametrize('base_accounts', [['0x15718b9B0DAdE1C17d8329A13bB9553f3B38e172']])
def test_swap_eth_to_token(base_inquirer, base_accounts, base_transaction_decoder):
    base_inquirer.ensure_cache_data_is_updated(
        cache_type=CacheType.AERODROME_POOL_ADDRESS,
        query_method=query_aerodrome_data,
        save_method=save_aerodrome_data_to_cache,
    )  # populates cache, addressbook and assets tables
    """Check that swapping eth to token in aerodrome is properly decoded."""
    evmhash = deserialize_evm_tx_hash('0xfef201a317bc156bf4b29f053372cbe0fd538920423cc43aaf09727f10ae3042')  # noqa: E501
    user_address = base_accounts[0]
    events, _ = get_decoded_events_of_transaction(
        evm_inquirer=base_transaction_decoder.evm_inquirer,
        database=base_transaction_decoder.database,
        tx_hash=evmhash,
    )
    timestamp = TimestampMS(1696541031000)
    expected_events = [
        EvmEvent(
            tx_hash=evmhash,
            sequence_index=0,
            timestamp=timestamp,
            location=Location.BASE,
            event_type=HistoryEventType.SPEND,
            event_subtype=HistoryEventSubType.FEE,
            asset=A_ETH,
            balance=Balance(FVal('0.000032616099395201')),
            location_label=user_address,
            counterparty=CPT_GAS,
            notes='Burned 0.000032616099395201 ETH for gas',
        ), EvmEvent(
            tx_hash=evmhash,
            sequence_index=1,
            timestamp=timestamp,
            location=Location.BASE,
            event_type=HistoryEventType.TRADE,
            event_subtype=HistoryEventSubType.SPEND,
            asset=A_ETH,
            balance=Balance(FVal('0.0001')),
            location_label=user_address,
            counterparty=CPT_AERODROME,
            address=ROUTER,
            notes=f'Swap 0.0001 ETH in {CPT_AERODROME}',
        ), EvmEvent(
            tx_hash=evmhash,
            sequence_index=34,
            timestamp=timestamp,
            location=Location.BASE,
            event_type=HistoryEventType.TRADE,
            event_subtype=HistoryEventSubType.RECEIVE,
            asset=A_USDBC,
            balance=Balance(FVal('0.163519')),
            location_label=user_address,
            counterparty=CPT_AERODROME,
            address=string_to_evm_address('0x16119F4820f78189370a9Df276F725DCfa1fD007'),  # sAMM wUSDR/USDbC pool  # noqa: E501
            notes=f'Receive 0.163519 USDbC as the result of a swap in {CPT_AERODROME}',
        ),
    ]
    assert events == expected_events


@pytest.mark.vcr()
@pytest.mark.parametrize('base_accounts', [['0x15718b9B0DAdE1C17d8329A13bB9553f3B38e172']])
def test_swap_token_to_eth(base_inquirer, base_accounts, base_transaction_decoder):
    base_inquirer.ensure_cache_data_is_updated(
        cache_type=CacheType.AERODROME_POOL_ADDRESS,
        query_method=query_aerodrome_data,
        save_method=save_aerodrome_data_to_cache,
    )  # populates cache, addressbook and assets tables
    """Check that swapping token to eth in aerodrome is properly decoded."""
    evmhash = deserialize_evm_tx_hash('0xf820b1c5ee682ce8a485a7a9eb362bc803c75c67be4ac63f7346217502ceb352')  # noqa: E501
    user_address = base_accounts[0]
    events, _ = get_decoded_events_of_transaction(
        evm_inquirer=base_transaction_decoder.evm_inquirer,
        database=base_transaction_decoder.database,
        tx_hash=evmhash,
    )
    timestamp = TimestampMS(1696965205000)
    expected_events = [
        EvmEvent(
            tx_hash=evmhash,
            sequence_index=0,
            timestamp=timestamp,
            location=Location.BASE,
            event_type=HistoryEventType.SPEND,
            event_subtype=HistoryEventSubType.FEE,
            asset=A_ETH.resolve_to_asset_with_symbol(),
            balance=Balance(FVal('0.000065595143380398')),
            location_label=user_address,
            counterparty=CPT_GAS,
            notes='Burned 0.000065595143380398 ETH for gas',
        ), EvmEvent(
            tx_hash=evmhash,
            sequence_index=5,
            timestamp=timestamp,
            location=Location.BASE,
            event_type=HistoryEventType.TRADE,
            event_subtype=HistoryEventSubType.SPEND,
            asset=A_USDC_BASE,
            balance=Balance(FVal(0.01)),
            location_label=user_address,
            address=USDC_USDBC_POOL_ADDRESS,
            counterparty=CPT_AERODROME,
            notes=f'Swap 0.01 USDC in {CPT_AERODROME}',
        ), EvmEvent(
            tx_hash=evmhash,
            sequence_index=16,
            timestamp=timestamp,
            location=Location.BASE,
            event_type=HistoryEventType.TRADE,
            event_subtype=HistoryEventSubType.RECEIVE,
            asset=Asset(AERO_TOKEN).resolve_to_asset_with_symbol(),
            balance=Balance(FVal('0.429198109072566355')),
            location_label=user_address,
            counterparty=CPT_AERODROME,
            address=AERO_WUSDR_POOL_ADDRESS,
            notes=f'Receive 0.429198109072566355 AERO as the result of a swap in {CPT_AERODROME}',
        ),
    ]
    assert events == expected_events


@pytest.mark.vcr()
@pytest.mark.parametrize('base_accounts', [['0x15718b9B0DAdE1C17d8329A13bB9553f3B38e172']])
def test_swap_tokens(base_inquirer, base_accounts, base_transaction_decoder):
    base_inquirer.ensure_cache_data_is_updated(
        cache_type=CacheType.AERODROME_POOL_ADDRESS,
        query_method=query_aerodrome_data,
        save_method=save_aerodrome_data_to_cache,
    )  # populates cache, addressbook and assets tables
    """Check that swapping tokens in aerodrome is properly decoded."""
    evmhash = deserialize_evm_tx_hash('0xf820b1c5ee682ce8a485a7a9eb362bc803c75c67be4ac63f7346217502ceb352')  # noqa: E501
    user_address = base_accounts[0]
    events, _ = get_decoded_events_of_transaction(
        evm_inquirer=base_transaction_decoder.evm_inquirer,
        database=base_transaction_decoder.database,
        tx_hash=evmhash,
    )
    timestamp = TimestampMS(1696965205000)
    expected_events = [
        EvmEvent(
            tx_hash=evmhash,
            sequence_index=0,
            timestamp=timestamp,
            location=Location.BASE,
            event_type=HistoryEventType.SPEND,
            event_subtype=HistoryEventSubType.FEE,
            asset=A_ETH,
            balance=Balance(FVal('0.000065595143380398')),
            location_label=user_address,
            counterparty=CPT_GAS,
            notes='Burned 0.000065595143380398 ETH for gas',
        ), EvmEvent(
            tx_hash=evmhash,
            sequence_index=5,
            timestamp=timestamp,
            location=Location.BASE,
            event_type=HistoryEventType.TRADE,
            event_subtype=HistoryEventSubType.SPEND,
            asset=A_USDC_BASE,
            balance=Balance(FVal('0.01')),
            location_label=user_address,
            counterparty=CPT_AERODROME,
            address=USDC_USDBC_POOL_ADDRESS,
            notes=f'Swap 0.01 USDC in {CPT_AERODROME}',
        ), EvmEvent(
            tx_hash=evmhash,
            sequence_index=16,
            timestamp=timestamp,
            location=Location.BASE,
            event_type=HistoryEventType.TRADE,
            event_subtype=HistoryEventSubType.RECEIVE,
            asset=Asset(AERO_TOKEN),
            balance=Balance(FVal('0.429198109072566355')),
            location_label=user_address,
            counterparty=CPT_AERODROME,
            address=AERO_WUSDR_POOL_ADDRESS,
            notes=f'Receive 0.429198109072566355 AERO as the result of a swap in {CPT_AERODROME}',  # noqa: E501
        ),
    ]
    assert events == expected_events


@pytest.mark.vcr()
@pytest.mark.parametrize('base_accounts', [['0x15718b9B0DAdE1C17d8329A13bB9553f3B38e172']])
def test_stake_lp_token_to_gauge(base_inquirer, base_accounts, base_transaction_decoder):
    base_inquirer.ensure_cache_data_is_updated(
        cache_type=CacheType.AERODROME_POOL_ADDRESS,
        query_method=query_aerodrome_data,
        save_method=save_aerodrome_data_to_cache,
    )  # populates cache, addressbook and assets tables
    """Check that depositing lp tokens to a aerodrome gauge is properly decoded."""
    get_or_create_evm_token(  # the token is needed for the approval event to be created
        userdb=base_transaction_decoder.evm_inquirer.database,
        evm_address=string_to_evm_address('0xd25711EdfBf747efCE181442Cc1D8F5F8fc8a0D3'),
        chain_id=ChainID.BASE,
        protocol=AERODROME_POOL_PROTOCOL,
        symbol='vAMM-WETH/USDbC',
    )
    evmhash = deserialize_evm_tx_hash('0xd39fda206175090719a8374032931fe5b1c35c9a4006486ec6d1028df2021f11')  # noqa: E501
    user_address = base_accounts[0]
    events, _ = get_decoded_events_of_transaction(
        evm_inquirer=base_transaction_decoder.evm_inquirer,
        database=base_transaction_decoder.database,
        tx_hash=evmhash,
    )
    timestamp = TimestampMS(1696541513000)
    expected_events = [
        EvmEvent(
            tx_hash=evmhash,
            sequence_index=0,
            timestamp=timestamp,
            location=Location.BASE,
            event_type=HistoryEventType.SPEND,
            event_subtype=HistoryEventSubType.FEE,
            asset=A_ETH.resolve_to_asset_with_symbol(),
            balance=Balance(FVal('0.000013526978999949')),
            location_label=user_address,
            counterparty=CPT_GAS,
            notes='Burned 0.000013526978999949 ETH for gas',
        ), EvmEvent(
            tx_hash=evmhash,
            sequence_index=58,
            timestamp=timestamp,
            location=Location.BASE,
            event_type=HistoryEventType.INFORMATIONAL,
            event_subtype=HistoryEventSubType.APPROVE,
            asset=Asset(WETH_USDBC_LP_TOKEN).resolve_to_asset_with_symbol(),
            balance=Balance(FVal(0)),
            location_label=user_address,
            address=WETH_USDBC_GAUGE_ADDRESS,
            notes=f'Revoke vAMM-WETH/USDbC spending approval of {user_address} by {WETH_USDBC_GAUGE_ADDRESS}',  # noqa: E501
        ), EvmEvent(
            tx_hash=evmhash,
            sequence_index=59,
            timestamp=timestamp,
            location=Location.BASE,
            event_type=HistoryEventType.DEPOSIT,
            event_subtype=HistoryEventSubType.DEPOSIT_ASSET,
            asset=Asset(WETH_USDBC_LP_TOKEN).resolve_to_asset_with_symbol(),
            balance=Balance(FVal(0.000000004023175857)),
            location_label=user_address,
            counterparty=CPT_AERODROME,
            address=WETH_USDBC_GAUGE_ADDRESS,
            product=EvmProduct.GAUGE,
            notes=f'Deposit 0.000000004023175857 vAMM-WETH/USDbC into {WETH_USDBC_GAUGE_ADDRESS} aerodrome gauge',  # noqa: E501
        ),
    ]
    assert events == expected_events
    assert EvmToken(WETH_USDBC_LP_TOKEN).protocol == AERODROME_POOL_PROTOCOL


@pytest.mark.vcr()
@pytest.mark.parametrize('base_accounts', [['0x15718b9B0DAdE1C17d8329A13bB9553f3B38e172']])
def test_unstake_lp_token_to_gauge(base_inquirer, base_accounts, base_transaction_decoder):
    base_inquirer.ensure_cache_data_is_updated(
        cache_type=CacheType.AERODROME_POOL_ADDRESS,
        query_method=query_aerodrome_data,
        save_method=save_aerodrome_data_to_cache,
    )  # populates cache, addressbook and assets tables
    """Check that withdrawing lp tokens from a aerodrome gauge is properly decoded."""
    evmhash = deserialize_evm_tx_hash('0x11fdbeacef54cd347cd5720160de070aec29e0a3480f76c18fc292b54aedfb9f')  # noqa: E501
    user_address = base_accounts[0]
    events, _ = get_decoded_events_of_transaction(
        evm_inquirer=base_transaction_decoder.evm_inquirer,
        database=base_transaction_decoder.database,
        tx_hash=evmhash,
    )
    timestamp = TimestampMS(1696615123000)
    expected_events = [
        EvmEvent(
            tx_hash=evmhash,
            sequence_index=0,
            timestamp=timestamp,
            location=Location.BASE,
            event_type=HistoryEventType.SPEND,
            event_subtype=HistoryEventSubType.FEE,
            asset=A_ETH,
            balance=Balance(FVal('0.000013830217387726')),
            location_label=user_address,
            counterparty=CPT_GAS,
            notes='Burned 0.000013830217387726 ETH for gas',
        ), EvmEvent(
            tx_hash=evmhash,
            sequence_index=17,
            timestamp=timestamp,
            location=Location.BASE,
            event_type=HistoryEventType.WITHDRAWAL,
            event_subtype=HistoryEventSubType.REMOVE_ASSET,
            asset=Asset(WETH_USDBC_LP_TOKEN).resolve_to_asset_with_symbol(),
            balance=Balance(FVal('0.000000004023175857')),
            location_label=user_address,
            counterparty=CPT_AERODROME,
            address=WETH_USDBC_GAUGE_ADDRESS,
            notes=f'Withdraw 0.000000004023175857 vAMM-WETH/USDbC from {WETH_USDBC_GAUGE_ADDRESS} aerodrome gauge',  # noqa: E501
            product=EvmProduct.GAUGE,
        ),
    ]
    assert events == expected_events


@pytest.mark.vcr()
@pytest.mark.parametrize('base_accounts', [['0x15718b9B0DAdE1C17d8329A13bB9553f3B38e172']])
def test_get_reward_from_gauge(base_inquirer, base_accounts, base_transaction_decoder):
    base_inquirer.ensure_cache_data_is_updated(
        cache_type=CacheType.AERODROME_POOL_ADDRESS,
        query_method=query_aerodrome_data,
        save_method=save_aerodrome_data_to_cache,
    )  # populates cache, addressbook and assets tables
    """Check claiming rewards from a aerodrome gauge is properly decoded."""
    evmhash = deserialize_evm_tx_hash('0xb76b04618e243d672352ad70d7e6a0644169ba390c28f211b6c12ee036efa6b2')  # noqa: E501
    user_address = base_accounts[0]
    events, _ = get_decoded_events_of_transaction(
        evm_inquirer=base_transaction_decoder.evm_inquirer,
        database=base_transaction_decoder.database,
        tx_hash=evmhash,
    )
    timestamp = TimestampMS(1697037287000)
    gauge_address = WETH_USDBC_GAUGE_ADDRESS
    expected_events = [
        EvmEvent(
            tx_hash=evmhash,
            sequence_index=0,
            timestamp=timestamp,
            location=Location.BASE,
            event_type=HistoryEventType.SPEND,
            event_subtype=HistoryEventSubType.FEE,
            asset=A_ETH.resolve_to_asset_with_symbol(),
            balance=Balance(FVal('0.000023095393459593')),
            location_label=user_address,
            counterparty=CPT_GAS,
            notes='Burned 0.000023095393459593 ETH for gas',
        ), EvmEvent(
            tx_hash=evmhash,
            sequence_index=12,
            timestamp=timestamp,
            location=Location.BASE,
            event_type=HistoryEventType.WITHDRAWAL,
            event_subtype=HistoryEventSubType.REWARD,
            asset=Asset(AERO_TOKEN).resolve_to_asset_with_symbol(),
            balance=Balance(FVal('0.002217484317583327')),
            location_label=user_address,
            counterparty=CPT_AERODROME,
            address=gauge_address,
            notes=f'Receive 0.002217484317583327 AERO rewards from {gauge_address} aerodrome gauge',  # noqa: E501
            product=EvmProduct.GAUGE,
        ),
    ]
    assert events == expected_events

from typing import TYPE_CHECKING

from rotkehlchen.chain.ethereum.modules.thegraph.constants import CONTRACT_STAKING
from rotkehlchen.chain.evm.decoding.thegraph.decoder import ThegraphCommonDecoder
from rotkehlchen.constants.assets import A_GRT

if TYPE_CHECKING:
    from rotkehlchen.chain.ethereum.node_inquirer import EthereumInquirer
    from rotkehlchen.chain.evm.decoding.base import BaseDecoderTools
    from rotkehlchen.user_messages import MessagesAggregator


class ThegraphDecoder(ThegraphCommonDecoder):

    def __init__(
            self,
            ethereum_inquirer: 'EthereumInquirer',
            base_tools: 'BaseDecoderTools',
            msg_aggregator: 'MessagesAggregator',
    ) -> None:
        super().__init__(
            evm_inquirer=ethereum_inquirer,
            base_tools=base_tools,
            msg_aggregator=msg_aggregator,
            native_asset=A_GRT,
            staking_contract=CONTRACT_STAKING,
        )

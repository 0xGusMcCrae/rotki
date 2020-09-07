import { BigNumber } from 'bignumber.js';
import { Balance } from '@/services/types-api';

export interface BlockchainBalances {
  readonly per_account: {
    ETH: ApiEthBalances;
    BTC: ApiBalances;
  };
  readonly totals: ApiBalances;
}

export interface ApiBalance {
  readonly amount: string;
  readonly usd_value: string;
}

export interface ApiBalances {
  [account: string]: ApiBalance;
}

export interface ApiEthBalance {
  readonly assets: ApiBalances;
  readonly total_usd_value: string;
}

export interface ApiEthBalances {
  [account: string]: ApiEthBalance;
}

export interface EthBalance {
  readonly totalUsdValue: BigNumber;
  readonly assets: Balances;
}

export interface EthBalances {
  [account: string]: EthBalance;
}

export interface Balances {
  [account: string]: Balance;
}

export interface AccountBalance {
  readonly account: string;
  readonly amount: BigNumber;
  readonly usdValue: BigNumber;
}

export interface AssetBalance {
  readonly asset: string;
  readonly amount: BigNumber;
  readonly usdValue: BigNumber;
}

export interface ManualBalancesByLocation {
  location: string;
  usdValue: BigNumber;
}

export interface ManualBalanceByLocation {
  [location: string]: BigNumber;
}

export interface ApiAssetBalance {
  readonly amount: string;
  readonly usd_value: string;
}

export interface AssetBalances {
  [asset: string]: Balance;
}

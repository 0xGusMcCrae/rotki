import { Status } from '@/store/const';
import { DefiState } from '@/store/defi/types';
import { Zero } from '@/utils/bignumbers';

export const defaultState = (): DefiState => ({
  status: Status.NONE,
  defiStatus: Status.NONE,
  lendingHistoryStatus: Status.NONE,
  borrowingHistoryStatus: Status.NONE,
  dsrHistory: {},
  dsrBalances: {
    currentDSR: Zero,
    balances: {}
  },
  makerDAOVaults: [],
  makerDAOVaultDetails: [],
  aaveBalances: {},
  aaveHistory: {},
  allProtocols: {},
  compoundBalances: {},
  compoundHistory: {
    events: [],
    profitAndLoss: {}
  }
});

export const state: DefiState = defaultState();

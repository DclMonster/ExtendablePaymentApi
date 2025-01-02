import { AppleVerifier } from './appleVerifier';
import { CoinbaseVerifier } from './coinbaseVerifier';
import { CoinSubVerifier } from './coinsubVerifier';
import { GoogleVerifier } from './googleVerifier';
import { PaypalVerifier } from './paypalVerifier';

const coinsubVerifier = new CoinSubVerifier();
const paypalVerifier = new PaypalVerifier();
const googleVerifier = new GoogleVerifier();
const appleVerifier = new AppleVerifier();
const coinbaseVerifier = new CoinbaseVerifier();

export { coinsubVerifier, paypalVerifier, googleVerifier, appleVerifier, coinbaseVerifier };

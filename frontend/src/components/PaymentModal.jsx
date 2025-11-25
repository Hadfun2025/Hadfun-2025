import React, { useState } from 'react';
import { X, Loader2, Tag, Check } from 'lucide-react';
import axios from 'axios';

const API = process.env.REACT_APP_BACKEND_URL ? `${process.env.REACT_APP_BACKEND_URL}/api` : '/api';

export function PaymentModal({ isOpen, onClose, onPayment, userEmail, userName }) {
  const [selectedStake, setSelectedStake] = useState(0.0);
  const [isProcessing, setIsProcessing] = useState(false);
  const [promoCode, setPromoCode] = useState('');
  const [promoApplied, setPromoApplied] = useState(null);
  const [promoValidating, setPromoValidating] = useState(false);
  const [promoError, setPromoError] = useState('');

  if (!isOpen) return null;

  const stakeOptions = [
    { value: 0.0, label: 'Play for Free', popular: false, isFree: true, recommended: true, displayAmount: 'Free' },
    { value: 2.13, label: '£2 stake', popular: false, displayAmount: '£2.13', actualStake: 2.0 },
    { value: 3.15, label: '£3 stake', popular: true, displayAmount: '£3.15', actualStake: 3.0 },
    { value: 5.18, label: '£5 stake', popular: false, displayAmount: '£5.18', actualStake: 5.0 }
  ];

  const handleValidatePromo = async () => {
    if (!promoCode.trim()) {
      setPromoError('Please enter a promo code');
      return;
    }

    setPromoValidating(true);
    setPromoError('');

    try {
      const response = await axios.post(`${API}/promo-codes/validate`, {
        code: promoCode.toUpperCase(),
        user_email: userEmail
      });

      if (response.data.valid) {
        setPromoApplied(response.data);
        setPromoError('');
      } else {
        setPromoError(response.data.message || 'Invalid promo code');
        setPromoApplied(null);
      }
    } catch (error) {
      setPromoError(error.response?.data?.detail || 'Failed to validate promo code');
      setPromoApplied(null);
    } finally {
      setPromoValidating(false);
    }
  };

  const handleRemovePromo = () => {
    setPromoCode('');
    setPromoApplied(null);
    setPromoError('');
  };

  const calculateFinalAmount = (baseAmount) => {
    if (!promoApplied || baseAmount === 0) return baseAmount;

    const discount = promoApplied.discount_value || 0;
    const discountType = promoApplied.discount_type || 'fixed';

    if (discountType === 'fixed') {
      return Math.max(0, baseAmount - discount);
    } else {
      const discountAmount = baseAmount * (discount / 100);
      return Math.max(0, baseAmount - discountAmount);
    }
  };

  const handlePayment = async () => {
    setIsProcessing(true);
    try {
      const finalAmount = calculateFinalAmount(selectedStake);
      
      // Apply promo code if used
      if (promoApplied && selectedStake > 0) {
        try {
          await axios.post(`${API}/promo-codes/apply`, null, {
            params: {
              promo_code: promoCode.toUpperCase(),
              user_email: userEmail
            }
          });
        } catch (error) {
          console.error('Failed to record promo usage:', error);
        }
      }
      
      await onPayment(finalAmount, promoApplied ? promoCode.toUpperCase() : null);
    } catch (error) {
      console.error('Payment error:', error);
      setIsProcessing(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center">
      {/* Backdrop */}
      <div 
        className="absolute inset-0 bg-black bg-opacity-50"
        onClick={onClose}
      />
      
      {/* Modal */}
      <div className="relative bg-white rounded-lg shadow-xl max-w-md w-full mx-4 p-6 max-h-[90vh] overflow-y-auto">
        {/* Close button */}
        <button
          onClick={onClose}
          className="absolute top-4 right-4 text-gray-400 hover:text-gray-600"
        >
          <X className="w-5 h-5" />
        </button>

        {/* Header */}
        <div className="mb-6">
          <h2 className="text-2xl font-bold text-gray-900">Choose Your Play Mode</h2>
          <p className="text-sm text-gray-600 mt-1">
            Play for fun, or add optional stakes for your group
          </p>
        </div>

        {/* Stake options */}
        <div className="space-y-3 mb-6">
          {stakeOptions.map((option) => (
              <div
                key={option.value}
                onClick={() => setSelectedStake(option.value)}
                className={`w-full p-4 rounded-lg border-2 text-left transition-all cursor-pointer ${
                  selectedStake === option.value
                    ? 'border-green-600 bg-green-50 shadow-md'
                    : 'border-gray-200 hover:border-green-300 hover:shadow-sm'
                }`}
              >
                <div className="flex justify-between items-center">
                  <div className="flex-1">
                    <div className="flex items-center gap-2 mb-1">
                      <span className="text-xl font-bold text-gray-900">
                        {option.displayAmount || option.label}
                      </span>
                      {option.popular && (
                        <span className="text-xs bg-green-600 text-white px-2 py-0.5 rounded-full">
                          Popular
                        </span>
                      )}
                      {option.recommended && (
                        <span className="text-xs bg-blue-600 text-white px-2 py-0.5 rounded-full">
                          Recommended
                        </span>
                      )}
                      {option.isFree && !option.recommended && (
                        <span className="text-xs bg-blue-600 text-white px-2 py-0.5 rounded-full">
                          Free
                        </span>
                      )}
                    </div>
                    {option.actualStake && (
                      <div className="text-xs text-gray-600 space-y-0.5">
                        <div className="flex justify-between max-w-[200px]">
                          <span>Stake:</span>
                          <span className="font-medium">£{option.actualStake.toFixed(2)}</span>
                        </div>
                        <div className="flex justify-between max-w-[200px]">
                          <span>Processing (shared):</span>
                          <span className="font-medium">£{(option.value - option.actualStake).toFixed(2)}</span>
                        </div>
                        <div className="flex justify-between max-w-[200px] pt-1 border-t border-gray-300">
                          <span className="font-semibold">Total:</span>
                          <span className="font-semibold">£{option.value.toFixed(2)}</span>
                        </div>
                      </div>
                    )}
                    {!option.actualStake && (
                      <p className="text-sm text-gray-600">
                        {option.isFree 
                          ? 'Just for fun - no stakes needed!'
                          : 'Optional: add stakes to your group competition'
                        }
                      </p>
                    )}
                  </div>
                  <div className={`w-5 h-5 rounded-full border-2 flex-shrink-0 ${
                    selectedStake === option.value
                      ? 'border-green-600 bg-green-600'
                      : 'border-gray-300'
                  }`}>
                    {selectedStake === option.value && (
                      <div className="w-full h-full flex items-center justify-center">
                        <div className="w-2 h-2 bg-white rounded-full" />
                      </div>
                    )}
                  </div>
                </div>
              </div>
          ))}
        </div>

        {/* Promo Code Section - Only show for paid stakes */}
        {selectedStake > 0 && (
          <div className="mb-6 p-4 bg-gradient-to-r from-purple-50 to-pink-50 border border-purple-200 rounded-lg">
            <div className="flex items-center gap-2 mb-3">
              <Tag className="w-5 h-5 text-purple-600" />
              <span className="font-semibold text-purple-900">Have a Promo Code?</span>
            </div>
            
            {!promoApplied ? (
              <div className="space-y-2">
                <div className="flex gap-2">
                  <input
                    type="text"
                    value={promoCode}
                    onChange={(e) => setPromoCode(e.target.value.toUpperCase())}
                    placeholder="Enter code (e.g., LAUNCH2025)"
                    className="flex-1 px-3 py-2 border border-purple-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-purple-500 uppercase"
                    disabled={promoValidating}
                  />
                  <button
                    onClick={handleValidatePromo}
                    disabled={promoValidating || !promoCode.trim()}
                    className="px-4 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700 disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2"
                  >
                    {promoValidating ? (
                      <>
                        <Loader2 className="w-4 h-4 animate-spin" />
                        <span>Checking...</span>
                      </>
                    ) : (
                      <span>Apply</span>
                    )}
                  </button>
                </div>
                {promoError && (
                  <p className="text-sm text-red-600">❌ {promoError}</p>
                )}
              </div>
            ) : (
              <div className="bg-white border border-green-500 rounded-lg p-3">
                <div className="flex justify-between items-start">
                  <div className="flex-1">
                    <div className="flex items-center gap-2 mb-1">
                      <Check className="w-5 h-5 text-green-600" />
                      <span className="font-semibold text-green-900">{promoCode.toUpperCase()} Applied!</span>
                    </div>
                    <p className="text-sm text-gray-600">{promoApplied.description}</p>
                    <p className="text-sm font-semibold text-green-700 mt-1">
                      Discount: £{promoApplied.discount_value?.toFixed(2) || '0.00'}
                    </p>
                  </div>
                  <button
                    onClick={handleRemovePromo}
                    className="text-gray-400 hover:text-red-600 ml-2"
                  >
                    <X className="w-5 h-5" />
                  </button>
                </div>
              </div>
            )}
          </div>
        )}

        {/* Payment Summary - Show discount if promo applied */}
        {selectedStake > 0 && promoApplied && (
          <div className="mb-6 p-4 bg-green-50 border border-green-200 rounded-lg">
            <div className="space-y-2 text-sm">
              <div className="flex justify-between text-gray-700">
                <span>Original Amount:</span>
                <span>£{selectedStake.toFixed(2)}</span>
              </div>
              <div className="flex justify-between text-green-700 font-medium">
                <span>Promo Discount ({promoCode.toUpperCase()}):</span>
                <span>-£{promoApplied.discount_value?.toFixed(2) || '0.00'}</span>
              </div>
              <div className="flex justify-between text-lg font-bold text-green-900 pt-2 border-t border-green-300">
                <span>You Pay:</span>
                <span>£{calculateFinalAmount(selectedStake).toFixed(2)}</span>
              </div>
            </div>
          </div>
        )}

        {/* Info box */}
        <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 mb-6">
          <p className="text-sm text-blue-900">
            <strong>How it works:</strong>
          </p>
          <ul className="text-sm text-blue-800 mt-2 space-y-1">
            <li>• Payment processing fees shared 50/50</li>
            <li>• 10% admin fee deducted from pot</li>
            <li>• Winner takes all remaining pot</li>
            <li>• Ties result in pot rollover</li>
            <li>• Predictions close Wednesday 11:59 PM</li>
          </ul>
        </div>

        {/* Action buttons */}
        <div className="flex gap-3">
          <button
            onClick={onClose}
            className="flex-1 px-4 py-2 border border-gray-300 rounded-lg text-gray-700 hover:bg-gray-50"
            disabled={isProcessing}
          >
            Cancel
          </button>
          <button
            onClick={handlePayment}
            disabled={isProcessing}
            className="flex-1 px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 disabled:bg-gray-400 disabled:cursor-not-allowed flex items-center justify-center"
          >
            {isProcessing ? (
              <>
                <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                Processing...
              </>
            ) : selectedStake === 0.0 ? (
              'Play for Fun'
            ) : promoApplied ? (
              `Pay £${calculateFinalAmount(selectedStake).toFixed(2)} (Promo Applied!)`
            ) : (
              `Pay ${stakeOptions.find(opt => opt.value === selectedStake)?.displayAmount || `£${selectedStake.toFixed(2)}`}`
            )}
          </button>
        </div>
      </div>
    </div>
  );
}

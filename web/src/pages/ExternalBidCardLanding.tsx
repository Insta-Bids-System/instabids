import React, { useState, useEffect } from 'react';
import { useSearchParams, useNavigate } from 'react-router-dom';
import { motion, AnimatePresence } from 'framer-motion';
import { 
  Calendar, 
  Clock, 
  MapPin, 
  DollarSign, 
  Users, 
  CheckCircle, 
  ArrowRight, 
  Star,
  Camera,
  Zap,
  Shield,
  Target,
  TrendingUp,
  Award
} from 'lucide-react';

interface BidCard {
  id: string;
  public_token: string;
  project_type: string;
  urgency: string;
  budget_display: string;
  location: {
    city: string;
    state: string;
  };
  contractor_count: number;
  created_at: string;
  photo_urls?: string[];
  project_details?: {
    scope_of_work?: string[];
    property_details?: any;
  };
}

const ExternalBidCardLanding: React.FC = () => {
  const [searchParams] = useSearchParams();
  const navigate = useNavigate();
  const [bidCard, setBidCard] = useState<BidCard | null>(null);
  const [loading, setLoading] = useState(true);
  const [currentPhotoIndex, setCurrentPhotoIndex] = useState(0);
  const [formData, setFormData] = useState({
    firstName: '',
    lastName: '',
    email: '',
    phone: '',
    company: '',
    trade: '',
    zipCode: ''
  });

  const bidToken = searchParams.get('bid');
  const source = searchParams.get('src') || 'direct';

  useEffect(() => {
    if (bidToken) {
      trackBidCardClick(bidToken, source);
      loadBidCard(bidToken);
    } else {
      setLoading(false);
    }
  }, [bidToken, source]);

  // Auto-rotate photos
  useEffect(() => {
    if (bidCard?.photo_urls && bidCard.photo_urls.length > 1) {
      const interval = setInterval(() => {
        setCurrentPhotoIndex((prev) => 
          prev === bidCard.photo_urls!.length - 1 ? 0 : prev + 1
        );
      }, 4000);
      return () => clearInterval(interval);
    }
  }, [bidCard?.photo_urls]);

  const trackBidCardClick = async (token: string, source: string) => {
    try {
      await fetch('/api/track/bid-card-click', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          bid_token: token,
          source_channel: source,
          user_agent: navigator.userAgent
        })
      });
    } catch (error) {
      console.error('Failed to track click:', error);
    }
  };

  const loadBidCard = async (token: string) => {
    try {
      const response = await fetch(`/api/bid-cards/by-token/${token}`);
      if (response.ok) {
        const data = await response.json();
        setBidCard(data);
      }
    } catch (error) {
      console.error('Failed to load bid card:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    try {
      const response = await fetch('/api/contractors/signup', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          ...formData,
          source: source,
          bid_context: bidToken
        })
      });

      if (response.ok) {
        const contractor = await response.json();
        
        await fetch('/api/track/bid-card-conversion', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            bid_token: bidToken,
            contractor_id: contractor.id
          })
        });

        navigate('/contractor/welcome');
      }
    } catch (error) {
      console.error('Signup failed:', error);
    }
  };

  const formatProjectType = (type: string) => {
    return type.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase());
  };

  const getUrgencyColor = (urgency: string) => {
    switch (urgency?.toLowerCase()) {
      case 'emergency':
        return 'from-red-500 to-red-600';
      case 'week':
        return 'from-orange-500 to-orange-600';
      case 'month':
        return 'from-blue-500 to-blue-600';
      default:
        return 'from-gray-500 to-gray-600';
    }
  };

  const getUrgencyText = (urgency: string) => {
    switch (urgency?.toLowerCase()) {
      case 'emergency':
        return 'Urgent - ASAP';
      case 'week':
        return 'Within 7 Days';
      case 'month':
        return 'Within 30 Days';
      default:
        return 'Flexible Timeline';
    }
  };

  const commonTrades = [
    'General Contractor', 'Electrician', 'Plumber', 'HVAC', 'Carpenter',
    'Painter', 'Roofer', 'Landscaper', 'Handyman', 'Other'
  ];

  const benefits = [
    {
      icon: Shield,
      title: "Zero Lead Fees",
      description: "Submit unlimited quotes for free. Pay only when you win the job.",
      gradient: "from-green-400 to-green-600"
    },
    {
      icon: Target,
      title: "Pre-Qualified Projects",
      description: "Every homeowner has confirmed budget and is ready to hire immediately.",
      gradient: "from-blue-400 to-blue-600"
    },
    {
      icon: TrendingUp,
      title: "Higher Win Rates",
      description: "Our contractors average 40% higher win rates than industry standard.",
      gradient: "from-purple-400 to-purple-600"
    },
    {
      icon: Zap,
      title: "Instant Notifications",
      description: "Get notified within minutes of new projects in your area.",
      gradient: "from-yellow-400 to-yellow-600"
    }
  ];

  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900 flex items-center justify-center">
        <motion.div 
          className="text-center"
          initial={{ opacity: 0, scale: 0.8 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ duration: 0.6 }}
        >
          <motion.div 
            className="w-16 h-16 border-4 border-white border-t-transparent rounded-full mx-auto mb-4"
            animate={{ rotate: 360 }}
            transition={{ duration: 1, repeat: Infinity, ease: "linear" }}
          />
          <p className="text-xl text-white">Loading your project...</p>
        </motion.div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900 overflow-hidden">
      {/* Background Effects */}
      <div className="absolute inset-0 overflow-hidden">
        <div className="absolute -top-40 -right-40 w-80 h-80 bg-purple-500 rounded-full mix-blend-multiply filter blur-xl opacity-20 animate-pulse"></div>
        <div className="absolute -bottom-40 -left-40 w-80 h-80 bg-blue-500 rounded-full mix-blend-multiply filter blur-xl opacity-20 animate-pulse"></div>
        <div className="absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2 w-80 h-80 bg-pink-500 rounded-full mix-blend-multiply filter blur-xl opacity-10 animate-pulse"></div>
      </div>

      <div className="relative z-10">
        {/* Hero Section */}
        <motion.div 
          className="text-center pt-20 pb-16 px-4"
          initial={{ opacity: 0, y: -50 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8 }}
        >
          <motion.div
            className="inline-flex items-center gap-2 bg-gradient-to-r from-purple-500/20 to-blue-500/20 backdrop-blur-sm rounded-full px-6 py-2 mb-8 border border-white/10"
            initial={{ opacity: 0, scale: 0.8 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ delay: 0.2, duration: 0.6 }}
          >
            <Award className="w-5 h-5 text-yellow-400" />
            <span className="text-sm text-white/90">Trusted by 10,000+ contractors</span>
          </motion.div>

          <motion.h1 
            className="text-5xl md:text-7xl font-bold text-white mb-6"
            initial={{ opacity: 0, y: 30 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.3, duration: 0.8 }}
          >
            Join InstaBids
            <span className="block bg-gradient-to-r from-blue-400 to-purple-400 bg-clip-text text-transparent">
              Submit Quotes for Free
            </span>
          </motion.h1>

          <motion.p 
            className="text-xl md:text-2xl text-white/80 mb-8 max-w-2xl mx-auto"
            initial={{ opacity: 0, y: 30 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.4, duration: 0.8 }}
          >
            No longer pay for leads, only jobs
          </motion.p>

          {/* Stats */}
          <motion.div 
            className="flex justify-center gap-8 md:gap-16 mb-16"
            initial={{ opacity: 0, y: 30 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.5, duration: 0.8 }}
          >
            {[
              { label: "Projects Available", value: "500+" },
              { label: "Active Contractors", value: "10K+" },
              { label: "Jobs Completed", value: "$50M+" }
            ].map((stat, index) => (
              <motion.div 
                key={index}
                className="text-center"
                whileHover={{ scale: 1.05 }}
                transition={{ type: "spring", stiffness: 400, damping: 10 }}
              >
                <div className="text-3xl md:text-4xl font-bold text-white mb-2">{stat.value}</div>
                <div className="text-sm text-white/60">{stat.label}</div>
              </motion.div>
            ))}
          </motion.div>
        </motion.div>

        {/* Dynamic Bid Card Showcase */}
        {bidCard && (
          <motion.div 
            className="max-w-6xl mx-auto px-4 mb-20"
            initial={{ opacity: 0, y: 50 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.6, duration: 0.8 }}
          >
            <motion.div 
              className="bg-white/10 backdrop-blur-lg rounded-3xl p-8 border border-white/20 shadow-2xl"
              whileHover={{ y: -5 }}
              transition={{ type: "spring", stiffness: 300, damping: 30 }}
            >
              <div className="flex items-center gap-3 mb-6">
                <motion.div
                  className="w-3 h-3 bg-green-400 rounded-full"
                  animate={{ scale: [1, 1.2, 1] }}
                  transition={{ duration: 2, repeat: Infinity }}
                />
                <span className="text-green-400 font-semibold">New Project Available</span>
              </div>

              <div className="grid lg:grid-cols-2 gap-8">
                {/* Project Details */}
                <div>
                  <motion.h2 
                    className="text-3xl md:text-4xl font-bold text-white mb-4"
                    initial={{ opacity: 0, x: -30 }}
                    animate={{ opacity: 1, x: 0 }}
                    transition={{ delay: 0.7, duration: 0.6 }}
                  >
                    {formatProjectType(bidCard.project_type)}
                  </motion.h2>

                  <motion.div
                    className={`inline-flex items-center gap-2 px-4 py-2 rounded-full text-white font-medium bg-gradient-to-r ${getUrgencyColor(bidCard.urgency)} mb-6`}
                    initial={{ opacity: 0, scale: 0.8 }}
                    animate={{ opacity: 1, scale: 1 }}
                    transition={{ delay: 0.8, duration: 0.6 }}
                  >
                    <Clock className="w-4 h-4" />
                    {getUrgencyText(bidCard.urgency)}
                  </motion.div>

                  <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
                    {[
                      { icon: MapPin, label: `${bidCard.location.city}, ${bidCard.location.state}` },
                      { icon: DollarSign, label: bidCard.budget_display },
                      { icon: Users, label: `${bidCard.contractor_count} needed` }
                    ].map((item, index) => (
                      <motion.div 
                        key={index}
                        className="flex items-center gap-2 text-white/90"
                        initial={{ opacity: 0, x: -20 }}
                        animate={{ opacity: 1, x: 0 }}
                        transition={{ delay: 0.9 + index * 0.1, duration: 0.6 }}
                      >
                        <item.icon className="w-5 h-5 text-blue-400" />
                        <span>{item.label}</span>
                      </motion.div>
                    ))}
                  </div>

                  {bidCard.project_details?.scope_of_work && (
                    <motion.div
                      initial={{ opacity: 0, y: 20 }}
                      animate={{ opacity: 1, y: 0 }}
                      transition={{ delay: 1.2, duration: 0.6 }}
                    >
                      <h3 className="text-lg font-semibold text-white mb-3">Project Scope:</h3>
                      <ul className="space-y-2">
                        {bidCard.project_details.scope_of_work.slice(0, 3).map((item, index) => (
                          <motion.li 
                            key={index}
                            className="flex items-start gap-2 text-white/80"
                            initial={{ opacity: 0, x: -20 }}
                            animate={{ opacity: 1, x: 0 }}
                            transition={{ delay: 1.3 + index * 0.1, duration: 0.6 }}
                          >
                            <CheckCircle className="w-4 h-4 text-green-400 mt-0.5 flex-shrink-0" />
                            <span>{item}</span>
                          </motion.li>
                        ))}
                      </ul>
                    </motion.div>
                  )}
                </div>

                {/* Photo Gallery */}
                {bidCard.photo_urls && bidCard.photo_urls.length > 0 && (
                  <motion.div 
                    className="relative"
                    initial={{ opacity: 0, scale: 0.9 }}
                    animate={{ opacity: 1, scale: 1 }}
                    transition={{ delay: 1.0, duration: 0.8 }}
                  >
                    <div className="relative h-80 rounded-2xl overflow-hidden">
                      <AnimatePresence mode="wait">
                        <motion.img
                          key={currentPhotoIndex}
                          src={bidCard.photo_urls[currentPhotoIndex]}
                          alt={`Project photo ${currentPhotoIndex + 1}`}
                          className="w-full h-full object-cover"
                          initial={{ opacity: 0, scale: 1.1 }}
                          animate={{ opacity: 1, scale: 1 }}
                          exit={{ opacity: 0, scale: 0.9 }}
                          transition={{ duration: 0.5 }}
                        />
                      </AnimatePresence>
                      
                      {/* Photo Count Badge */}
                      <div className="absolute top-4 right-4 bg-black/50 backdrop-blur-sm rounded-full px-3 py-1 flex items-center gap-1">
                        <Camera className="w-4 h-4 text-white" />
                        <span className="text-white text-sm">{bidCard.photo_urls.length}</span>
                      </div>

                      {/* Photo Navigation Dots */}
                      {bidCard.photo_urls.length > 1 && (
                        <div className="absolute bottom-4 left-1/2 transform -translate-x-1/2 flex gap-2">
                          {bidCard.photo_urls.map((_, index) => (
                            <button
                              key={index}
                              onClick={() => setCurrentPhotoIndex(index)}
                              className={`w-2 h-2 rounded-full transition-all ${
                                index === currentPhotoIndex ? 'bg-white' : 'bg-white/40'
                              }`}
                            />
                          ))}
                        </div>
                      )}
                    </div>
                  </motion.div>
                )}
              </div>
            </motion.div>
          </motion.div>
        )}

        {/* Benefits Section */}
        <motion.div 
          className="max-w-6xl mx-auto px-4 mb-20"
          initial={{ opacity: 0, y: 50 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.8, duration: 0.8 }}
        >
          <div className="text-center mb-12">
            <h2 className="text-3xl md:text-4xl font-bold text-white mb-4">
              Why Top Contractors Choose InstaBids
            </h2>
            <p className="text-xl text-white/70">
              Join thousands of contractors who've revolutionized their business
            </p>
          </div>

          <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-6">
            {benefits.map((benefit, index) => (
              <motion.div
                key={index}
                className="bg-white/5 backdrop-blur-sm rounded-2xl p-6 border border-white/10 hover:bg-white/10 transition-all duration-300"
                initial={{ opacity: 0, y: 30 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 1.0 + index * 0.1, duration: 0.6 }}
                whileHover={{ y: -5, scale: 1.02 }}
              >
                <div className={`w-12 h-12 rounded-xl bg-gradient-to-br ${benefit.gradient} flex items-center justify-center mb-4`}>
                  <benefit.icon className="w-6 h-6 text-white" />
                </div>
                <h3 className="text-lg font-semibold text-white mb-2">{benefit.title}</h3>
                <p className="text-white/70 text-sm">{benefit.description}</p>
              </motion.div>
            ))}
          </div>
        </motion.div>

        {/* Signup Form */}
        <motion.div 
          className="max-w-2xl mx-auto px-4 pb-20"
          initial={{ opacity: 0, y: 50 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 1.0, duration: 0.8 }}
        >
          <div className="bg-white/10 backdrop-blur-lg rounded-3xl p-8 border border-white/20">
            <div className="text-center mb-8">
              <h2 className="text-3xl font-bold text-white mb-4">Start Winning More Jobs Today</h2>
              <p className="text-white/70">Join in under 2 minutes. Start bidding immediately.</p>
            </div>

            <form onSubmit={handleSubmit} className="space-y-6">
              <div className="grid grid-cols-2 gap-4">
                {[
                  { name: 'firstName', label: 'First Name', type: 'text' },
                  { name: 'lastName', label: 'Last Name', type: 'text' }
                ].map((field, index) => (
                  <motion.div 
                    key={field.name}
                    initial={{ opacity: 0, x: index === 0 ? -20 : 20 }}
                    animate={{ opacity: 1, x: 0 }}
                    transition={{ delay: 1.2 + index * 0.1, duration: 0.6 }}
                  >
                    <label className="block text-sm font-medium text-white/90 mb-2">
                      {field.label} *
                    </label>
                    <input
                      type={field.type}
                      name={field.name}
                      required
                      value={formData[field.name as keyof typeof formData]}
                      onChange={handleInputChange}
                      className="w-full px-4 py-3 bg-white/10 border border-white/20 rounded-xl text-white placeholder-white/50 focus:ring-2 focus:ring-blue-500 focus:border-transparent backdrop-blur-sm transition-all"
                    />
                  </motion.div>
                ))}
              </div>

              {[
                { name: 'email', label: 'Email Address', type: 'email' },
                { name: 'phone', label: 'Phone Number', type: 'tel' },
                { name: 'company', label: 'Company Name', type: 'text', required: false },
                { name: 'zipCode', label: 'Service Area ZIP Code', type: 'text' }
              ].map((field, index) => (
                <motion.div 
                  key={field.name}
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: 1.4 + index * 0.1, duration: 0.6 }}
                >
                  <label className="block text-sm font-medium text-white/90 mb-2">
                    {field.label} {field.required !== false && '*'}
                  </label>
                  <input
                    type={field.type}
                    name={field.name}
                    required={field.required !== false}
                    value={formData[field.name as keyof typeof formData]}
                    onChange={handleInputChange}
                    className="w-full px-4 py-3 bg-white/10 border border-white/20 rounded-xl text-white placeholder-white/50 focus:ring-2 focus:ring-blue-500 focus:border-transparent backdrop-blur-sm transition-all"
                  />
                </motion.div>
              ))}

              <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 1.8, duration: 0.6 }}
              >
                <label className="block text-sm font-medium text-white/90 mb-2">
                  Primary Trade *
                </label>
                <select
                  name="trade"
                  required
                  value={formData.trade}
                  onChange={handleInputChange}
                  className="w-full px-4 py-3 bg-white/10 border border-white/20 rounded-xl text-white focus:ring-2 focus:ring-blue-500 focus:border-transparent backdrop-blur-sm transition-all"
                >
                  <option value="" className="bg-gray-800">Select your trade</option>
                  {commonTrades.map(trade => (
                    <option key={trade} value={trade} className="bg-gray-800">{trade}</option>
                  ))}
                </select>
              </motion.div>

              <motion.button
                type="submit"
                className="w-full bg-gradient-to-r from-blue-600 to-purple-600 text-white py-4 px-8 rounded-xl font-bold text-lg hover:from-blue-700 hover:to-purple-700 transition-all duration-300 flex items-center justify-center gap-2 shadow-lg"
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 1.9, duration: 0.6 }}
                whileHover={{ scale: 1.02 }}
                whileTap={{ scale: 0.98 }}
              >
                Join InstaBids - Start Winning Jobs
                <ArrowRight className="w-5 h-5" />
              </motion.button>

              <motion.p 
                className="text-xs text-white/50 text-center"
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                transition={{ delay: 2.0, duration: 0.6 }}
              >
                By signing up, you agree to our Terms of Service and Privacy Policy.
              </motion.p>
            </form>
          </div>
        </motion.div>
      </div>
    </div>
  );
};

export default ExternalBidCardLanding;
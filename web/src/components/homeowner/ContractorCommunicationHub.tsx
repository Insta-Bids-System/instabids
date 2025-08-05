import React, { useEffect, useState } from 'react';
import {
  MessageSquare,
  FileText,
  Image,
  User,
  Calendar,
  DollarSign,
  Clock,
  ChevronDown,
  ChevronUp,
  Send,
  Paperclip,
  Download,
  CheckCircle,
  AlertCircle
} from 'lucide-react';
import toast from 'react-hot-toast';

interface ContractorProposal {
  id: string;
  contractor_id: string;
  contractor_name: string;
  contractor_company?: string;
  bid_amount: number;
  timeline_days: number;
  proposal_text: string;
  attachments?: Array<{
    name: string;
    url: string;
    type: string;
    size: number;
  }>;
  submitted_at: string;
  status: 'pending' | 'accepted' | 'rejected';
}

interface Message {
  id: string;
  sender_type: 'contractor' | 'homeowner';
  sender_id: string;
  content: string;
  filtered_content: string;
  attachments?: Array<{
    url: string;
    type: string;
    name: string;
  }>;
  created_at: string;
  read: boolean;
}

interface Conversation {
  id: string;
  contractor_id: string;
  contractor_alias: string;
  last_message_at: string;
  homeowner_unread_count: number;
  messages: Message[];
}

interface ContractorInteraction {
  contractor_id: string;
  contractor_name: string;
  contractor_company?: string;
  proposal?: ContractorProposal;
  conversation?: Conversation;
  total_messages: number;
  unread_messages: number;
  has_attachments: boolean;
  last_interaction: string;
}

interface Props {
  bidCardId: string;
  homeownerId: string;
}

const ContractorCommunicationHub: React.FC<Props> = ({ bidCardId, homeownerId }) => {
  const [interactions, setInteractions] = useState<ContractorInteraction[]>([]);
  const [loading, setLoading] = useState(true);
  const [expandedContractor, setExpandedContractor] = useState<string | null>(null);
  const [selectedConversation, setSelectedConversation] = useState<string | null>(null);
  const [messageInput, setMessageInput] = useState('');
  const [sending, setSending] = useState(false);

  useEffect(() => {
    loadContractorInteractions();
  }, [bidCardId]);

  const loadContractorInteractions = async () => {
    try {
      setLoading(true);

      // Load proposals
      const proposalsResponse = await fetch(
        `http://localhost:8008/api/contractor-proposals/bid-card/${bidCardId}`
      );
      const proposals = proposalsResponse.ok ? await proposalsResponse.json() : [];

      // Load conversations
      const conversationsResponse = await fetch(
        `http://localhost:8008/api/messages/conversations?bid_card_id=${bidCardId}&user_type=homeowner&user_id=${homeownerId}`
      );
      const conversationsData = conversationsResponse.ok ? await conversationsResponse.json() : { conversations: [] };
      const conversations = conversationsData.conversations || [];

      // Group by contractor
      const contractorMap = new Map<string, ContractorInteraction>();

      // Add proposals
      proposals.forEach((proposal: ContractorProposal) => {
        contractorMap.set(proposal.contractor_id, {
          contractor_id: proposal.contractor_id,
          contractor_name: proposal.contractor_name,
          contractor_company: proposal.contractor_company,
          proposal,
          conversation: undefined,
          total_messages: 0,
          unread_messages: 0,
          has_attachments: proposal.attachments && proposal.attachments.length > 0,
          last_interaction: proposal.submitted_at
        });
      });

      // Add conversations
      for (const conv of conversations) {
        // Load messages for each conversation
        const messagesResponse = await fetch(
          `http://localhost:8008/api/messages/${conv.id}`
        );
        const messagesData = messagesResponse.ok ? await messagesResponse.json() : { messages: [] };
        conv.messages = messagesData.messages || [];

        const existing = contractorMap.get(conv.contractor_id);
        if (existing) {
          existing.conversation = conv;
          existing.total_messages = conv.messages.length;
          existing.unread_messages = conv.homeowner_unread_count;
          existing.has_attachments = existing.has_attachments || 
            conv.messages.some((m: Message) => m.attachments && m.attachments.length > 0);
          if (conv.last_message_at > existing.last_interaction) {
            existing.last_interaction = conv.last_message_at;
          }
        } else {
          contractorMap.set(conv.contractor_id, {
            contractor_id: conv.contractor_id,
            contractor_name: conv.contractor_alias || 'Contractor',
            contractor_company: undefined,
            proposal: undefined,
            conversation: conv,
            total_messages: conv.messages.length,
            unread_messages: conv.homeowner_unread_count,
            has_attachments: conv.messages.some((m: Message) => m.attachments && m.attachments.length > 0),
            last_interaction: conv.last_message_at
          });
        }
      }

      // Convert to array and sort by last interaction
      const interactionsList = Array.from(contractorMap.values()).sort(
        (a, b) => new Date(b.last_interaction).getTime() - new Date(a.last_interaction).getTime()
      );

      setInteractions(interactionsList);
    } catch (error) {
      console.error('Error loading contractor interactions:', error);
      toast.error('Failed to load contractor communications');
    } finally {
      setLoading(false);
    }
  };

  const sendMessage = async (conversationId: string, contractorId: string) => {
    if (!messageInput.trim()) return;

    try {
      setSending(true);
      const response = await fetch('http://localhost:8008/api/messages/send', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          conversation_id: conversationId,
          bid_card_id: bidCardId,
          homeowner_id: homeownerId,
          sender_type: 'homeowner',
          sender_id: homeownerId,
          content: messageInput
        })
      });

      if (response.ok) {
        toast.success('Message sent');
        setMessageInput('');
        // Reload to show new message
        await loadContractorInteractions();
      } else {
        throw new Error('Failed to send message');
      }
    } catch (error) {
      console.error('Error sending message:', error);
      toast.error('Failed to send message');
    } finally {
      setSending(false);
    }
  };

  const markMessagesAsRead = async (conversationId: string) => {
    try {
      await fetch(`http://localhost:8008/api/messages/${conversationId}/mark-read`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          user_type: 'homeowner',
          user_id: homeownerId
        })
      });
    } catch (error) {
      console.error('Error marking messages as read:', error);
    }
  };

  const toggleContractor = (contractorId: string) => {
    if (expandedContractor === contractorId) {
      setExpandedContractor(null);
      setSelectedConversation(null);
    } else {
      setExpandedContractor(contractorId);
      const interaction = interactions.find(i => i.contractor_id === contractorId);
      if (interaction?.conversation) {
        setSelectedConversation(interaction.conversation.id);
        markMessagesAsRead(interaction.conversation.id);
      }
    }
  };

  const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    const now = new Date();
    const diffMs = now.getTime() - date.getTime();
    const diffHours = Math.floor(diffMs / (1000 * 60 * 60));
    
    if (diffHours < 1) {
      const diffMinutes = Math.floor(diffMs / (1000 * 60));
      return `${diffMinutes} minute${diffMinutes !== 1 ? 's' : ''} ago`;
    } else if (diffHours < 24) {
      return `${diffHours} hour${diffHours !== 1 ? 's' : ''} ago`;
    } else {
      const diffDays = Math.floor(diffHours / 24);
      if (diffDays < 7) {
        return `${diffDays} day${diffDays !== 1 ? 's' : ''} ago`;
      } else {
        return date.toLocaleDateString();
      }
    }
  };

  const formatCurrency = (amount: number) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
      minimumFractionDigits: 0,
      maximumFractionDigits: 0
    }).format(amount);
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center p-8">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  if (interactions.length === 0) {
    return (
      <div className="text-center p-8 bg-gray-50 rounded-lg">
        <User className="w-12 h-12 text-gray-400 mx-auto mb-3" />
        <p className="text-gray-600">No contractor interactions yet</p>
        <p className="text-sm text-gray-500 mt-1">
          Contractors who submit bids or ask questions will appear here
        </p>
      </div>
    );
  }

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between mb-6">
        <h3 className="text-lg font-semibold text-gray-900">
          Contractor Communications
        </h3>
        <div className="text-sm text-gray-500">
          {interactions.length} contractor{interactions.length !== 1 ? 's' : ''}
        </div>
      </div>

      {interactions.map((interaction) => (
        <div
          key={interaction.contractor_id}
          className="bg-white border rounded-lg shadow-sm overflow-hidden"
        >
          {/* Contractor Header */}
          <div
            className="p-4 hover:bg-gray-50 cursor-pointer transition-colors"
            onClick={() => toggleContractor(interaction.contractor_id)}
          >
            <div className="flex items-center justify-between">
              <div className="flex items-center space-x-3">
                <div className="w-10 h-10 bg-blue-100 rounded-full flex items-center justify-center">
                  <User className="w-5 h-5 text-blue-600" />
                </div>
                <div>
                  <h4 className="font-medium text-gray-900">
                    {interaction.contractor_name}
                  </h4>
                  {interaction.contractor_company && (
                    <p className="text-sm text-gray-500">{interaction.contractor_company}</p>
                  )}
                </div>
              </div>

              <div className="flex items-center space-x-4">
                {/* Status Badges */}
                <div className="flex items-center space-x-2">
                  {interaction.proposal && (
                    <div className="flex items-center space-x-1 px-2 py-1 bg-green-100 rounded-full">
                      <FileText className="w-4 h-4 text-green-600" />
                      <span className="text-xs font-medium text-green-700">
                        Bid: {formatCurrency(interaction.proposal.bid_amount)}
                      </span>
                    </div>
                  )}
                  {interaction.unread_messages > 0 && (
                    <div className="flex items-center space-x-1 px-2 py-1 bg-blue-100 rounded-full">
                      <MessageSquare className="w-4 h-4 text-blue-600" />
                      <span className="text-xs font-medium text-blue-700">
                        {interaction.unread_messages} new
                      </span>
                    </div>
                  )}
                  {interaction.has_attachments && (
                    <div className="px-2 py-1 bg-gray-100 rounded-full">
                      <Paperclip className="w-4 h-4 text-gray-600" />
                    </div>
                  )}
                </div>

                <div className="text-sm text-gray-500">
                  {formatDate(interaction.last_interaction)}
                </div>

                {expandedContractor === interaction.contractor_id ? (
                  <ChevronUp className="w-5 h-5 text-gray-400" />
                ) : (
                  <ChevronDown className="w-5 h-5 text-gray-400" />
                )}
              </div>
            </div>
          </div>

          {/* Expanded Content */}
          {expandedContractor === interaction.contractor_id && (
            <div className="border-t">
              {/* Bid Proposal Section */}
              {interaction.proposal && (
                <div className="p-4 bg-gray-50 border-b">
                  <h5 className="font-medium text-gray-900 mb-3 flex items-center">
                    <FileText className="w-4 h-4 mr-2" />
                    Submitted Bid
                  </h5>
                  <div className="grid grid-cols-2 gap-4 mb-3">
                    <div>
                      <p className="text-sm text-gray-500">Bid Amount</p>
                      <p className="text-lg font-semibold text-gray-900">
                        {formatCurrency(interaction.proposal.bid_amount)}
                      </p>
                    </div>
                    <div>
                      <p className="text-sm text-gray-500">Timeline</p>
                      <p className="text-lg font-semibold text-gray-900">
                        {interaction.proposal.timeline_days} days
                      </p>
                    </div>
                  </div>
                  <div className="mb-3">
                    <p className="text-sm text-gray-500 mb-1">Proposal</p>
                    <p className="text-gray-700">{interaction.proposal.proposal_text}</p>
                  </div>
                  {interaction.proposal.attachments && interaction.proposal.attachments.length > 0 && (
                    <div>
                      <p className="text-sm text-gray-500 mb-2">Attachments</p>
                      <div className="space-y-2">
                        {interaction.proposal.attachments.map((attachment, index) => (
                          <a
                            key={index}
                            href={attachment.url}
                            target="_blank"
                            rel="noopener noreferrer"
                            className="flex items-center space-x-2 text-blue-600 hover:text-blue-700"
                          >
                            {attachment.type.startsWith('image/') ? (
                              <Image className="w-4 h-4" />
                            ) : (
                              <FileText className="w-4 h-4" />
                            )}
                            <span className="text-sm">{attachment.name}</span>
                            <Download className="w-3 h-3" />
                          </a>
                        ))}
                      </div>
                    </div>
                  )}
                </div>
              )}

              {/* Messages Section */}
              {interaction.conversation && (
                <div className="p-4">
                  <h5 className="font-medium text-gray-900 mb-3 flex items-center">
                    <MessageSquare className="w-4 h-4 mr-2" />
                    Messages
                  </h5>
                  
                  {/* Message Thread */}
                  <div className="space-y-3 mb-4 max-h-96 overflow-y-auto">
                    {interaction.conversation.messages.map((message) => (
                      <div
                        key={message.id}
                        className={`flex ${
                          message.sender_type === 'homeowner' ? 'justify-end' : 'justify-start'
                        }`}
                      >
                        <div
                          className={`max-w-xs lg:max-w-md px-4 py-2 rounded-lg ${
                            message.sender_type === 'homeowner'
                              ? 'bg-blue-600 text-white'
                              : 'bg-gray-100 text-gray-900'
                          }`}
                        >
                          <p className="text-sm">{message.filtered_content}</p>
                          {message.attachments && message.attachments.length > 0 && (
                            <div className="mt-2 space-y-1">
                              {message.attachments.map((attachment, index) => (
                                <a
                                  key={index}
                                  href={attachment.url}
                                  target="_blank"
                                  rel="noopener noreferrer"
                                  className={`flex items-center space-x-1 text-xs ${
                                    message.sender_type === 'homeowner'
                                      ? 'text-blue-100 hover:text-white'
                                      : 'text-blue-600 hover:text-blue-700'
                                  }`}
                                >
                                  {attachment.type.startsWith('image/') ? (
                                    <Image className="w-3 h-3" />
                                  ) : (
                                    <FileText className="w-3 h-3" />
                                  )}
                                  <span>{attachment.name}</span>
                                </a>
                              ))}
                            </div>
                          )}
                          <p
                            className={`text-xs mt-1 ${
                              message.sender_type === 'homeowner' ? 'text-blue-100' : 'text-gray-500'
                            }`}
                          >
                            {formatDate(message.created_at)}
                          </p>
                        </div>
                      </div>
                    ))}
                  </div>

                  {/* Message Input */}
                  <div className="flex space-x-2">
                    <input
                      type="text"
                      value={messageInput}
                      onChange={(e) => setMessageInput(e.target.value)}
                      onKeyPress={(e) => {
                        if (e.key === 'Enter' && !e.shiftKey) {
                          e.preventDefault();
                          sendMessage(interaction.conversation!.id, interaction.contractor_id);
                        }
                      }}
                      placeholder="Type your message..."
                      className="flex-1 px-3 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                      disabled={sending}
                    />
                    <button
                      onClick={() => sendMessage(interaction.conversation!.id, interaction.contractor_id)}
                      disabled={sending || !messageInput.trim()}
                      className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed"
                    >
                      {sending ? (
                        <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white"></div>
                      ) : (
                        <Send className="w-5 h-5" />
                      )}
                    </button>
                  </div>
                </div>
              )}

              {/* No Activity Message */}
              {!interaction.proposal && !interaction.conversation && (
                <div className="p-4 text-center text-gray-500">
                  <AlertCircle className="w-6 h-6 mx-auto mb-2 text-gray-400" />
                  <p className="text-sm">No communications from this contractor yet</p>
                </div>
              )}
            </div>
          )}
        </div>
      ))}
    </div>
  );
};

export default ContractorCommunicationHub;
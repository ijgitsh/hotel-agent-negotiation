import os
import random
import logging
from dataclasses import dataclass
from crewai import Agent, Task, Crew
from langchain_openai import ChatOpenAI
from langchain.schema import HumanMessage, SystemMessage
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Setup logging
logging.basicConfig(filename='negotiation_log.txt', level=logging.INFO, format='%(asctime)s - %(message)s')

@dataclass
class Hotel:
    name: str
    base_price: float
    min_margin: float  # as a percentage (e.g., 0.2 for 20%)
    llm_agent: Agent = None
    retry_count: int = 0
    max_retries: int = 2
    discount_step: float = 0.1  # Start with a 10% discount

    def calculate_min_acceptable_price(self):
        return round(self.base_price * (1 - self.min_margin), 2)

    def respond_to_offer(self, offer_price: float):
        min_price = self.calculate_min_acceptable_price()
        if offer_price >= min_price:
            return ("accept", offer_price)
        elif self.retry_count < self.max_retries:
            self.retry_count += 1
            counter_offer = round(min_price * (1 - self.discount_step), 2)
            self.discount_step += 0.1  # Increase discount step by 10%
            return ("counter", counter_offer)
        else:
            return ("reject", None)

class CustomerAgent:
    def __init__(self, initial_offer: float, max_rounds: int = 10):
        self.initial_offer = initial_offer
        self.max_rounds = max_rounds
        self.llm = ChatOpenAI(temperature=0)
        
        # Create an agent using the LLM directly
        self.agent = Agent(
            role="Customer Negotiator",
            goal="Negotiate best price with hotels",
            backstory="You are a budget-conscious traveler looking to book a hotel at the best possible price during the low season.",
            verbose=True,
            llm=self.llm,  # Pass the LLM directly
        )
        self.negotiation_summary = []

    def negotiate(self, hotels):
        offer = self.initial_offer
        best_offer = None
        best_price = float('inf')
        
        for round_num in range(1, self.max_rounds + 1):
            print(f"\n--- Round {round_num} ---")
            logging.info(f"Round {round_num}")
            responses = []
            all_rejected = True
            
            for hotel in hotels:
                status, price = hotel.respond_to_offer(offer)
                response_message = self.generate_dialogue(hotel, offer, status, price)
                print(f"{hotel.name} responds: {status.upper()}" + (f" with counter-offer ${price}" if status == "counter" else ""))
                print(f"🗨️  {hotel.name} says: {response_message}\n")
                logging.info(f"{hotel.name} responds: {status.upper()}" + (f" with counter-offer ${price}" if price else ""))
                logging.info(f"Dialogue: {response_message}")
                responses.append((hotel, status, price))
                self.negotiation_summary.append((round_num, hotel.name, status, price))
                
                if status != "reject":
                    all_rejected = False
                
                if status == "accept" and price < best_price:
                    best_offer = (hotel, price)
                    best_price = price
                elif status == "counter" and price < best_price:
                    best_offer = (hotel, price)
                    best_price = price

            if all_rejected:
                print("\n❌ All hotels rejected the offer.")
                logging.info("Failure: All hotels rejected the offer")
                self.print_summary()
                return None, None

            if best_offer and best_price <= self.initial_offer:
                print(f"\n✅ {best_offer[0].name} accepts the offer at ${best_offer[1]}!")
                logging.info(f"Success: {best_offer[0].name} accepts at ${best_offer[1]}")
                self.print_summary()
                return best_offer[0].name, best_offer[1]

            # Inform other hotels about the best offer received so far
            for hotel in hotels:
                if hotel != best_offer[0]:
                    status, price = hotel.respond_to_offer(best_price)
                    response_message = self.generate_dialogue(hotel, best_price, status, price)
                    print(f"{hotel.name} responds: {status.upper()}" + (f" with counter-offer ${price}" if status == "counter" else ""))
                    print(f"🗨️  {hotel.name} says: {response_message}\n")
                    logging.info(f"{hotel.name} responds: {status.upper()}" + (f" with counter-offer ${price}" if price else ""))
                    logging.info(f"Dialogue: {response_message}")
                    responses.append((hotel, status, price))
                    self.negotiation_summary.append((round_num, hotel.name, status, price))
                    
                    if status != "reject":
                        all_rejected = False
                    
                    if status == "accept" and price < best_price:
                        best_offer = (hotel, price)
                        best_price = price
                    elif status == "counter" and price < best_price:
                        best_offer = (hotel, price)
                        best_price = price

            if all_rejected:
                print("\n❌ All hotels rejected the offer.")
                logging.info("Failure: All hotels rejected the offer")
                self.print_summary()
                return None, None

            offer = best_price  # Use the best price as the new offer

        print("\n❌ No hotel accepted the offer after max rounds.")
        logging.info("Failure: No hotel accepted after max rounds")
        self.print_summary()
        return None, None

    def generate_dialogue(self, hotel, offer, status, price):
        if not hotel.llm_agent:
            return "[No agent dialogue configured]"
        
        try:
            # Use the LLM directly instead of the agent
            llm = ChatOpenAI(temperature=0)
            
            system_message = hotel.llm_agent.backstory
            
            task_prompt = (
                f"The customer offered ${offer}. You should respond with a short and realistic negotiation message. "
                f"Your stance is to {status} the offer." +
                (f" You counter with ${price}." if status == "counter" else "")
            )
            
            messages = [
                SystemMessage(content=system_message),
                HumanMessage(content=task_prompt)
            ]
            
            # Call the LLM directly
            response = llm.invoke(messages)
            return response.content
            
        except Exception as e:
            logging.error(f"Error generating dialogue: {str(e)}")
            return f"[Error generating response: {str(e)}]"

    def print_summary(self):
        print("\n📋 Negotiation Summary:")
        for round_num, hotel_name, status, price in self.negotiation_summary:
            status_str = f"{status.upper()}"
            if price:
                status_str += f" at ${price}"
            print(f"Round {round_num}: {hotel_name} -> {status_str}")

if __name__ == "__main__":
    try:
        initial_offer = float(input("Enter your initial offer (e.g., 65): "))
    except ValueError:
        print("Invalid input. Using default initial offer of $65.")
        initial_offer = 65

    # Create LLM for all agents
    llm = ChatOpenAI(temperature=0)

    hotel1 = Hotel(
        name="Hotel Azure",
        base_price=160,
        min_margin=0.1,
        llm_agent=Agent(
            role="Hotel Azure Agent",
            goal="Maximize booking profits while being flexible",
            backstory="You represent Hotel Azure, a modern seaside hotel that prefers not to leave rooms empty during the low season.",
            verbose=False,
            llm=llm,  # Pass the LLM directly
        )
    )

    hotel2 = Hotel(
        name="Sunset Lodge",
        base_price=155,
        min_margin=0.1,
        llm_agent=Agent(
            role="Sunset Lodge Agent",
            goal="Negotiate room prices but retain at least minimum profit",
            backstory="You represent Sunset Lodge, a cozy countryside retreat that welcomes negotiation in slow months.",
            verbose=False,
            llm=llm,  # Pass the LLM directly
        )
    )

    hotel3 = Hotel(
        name="Mountain View Inn",
        base_price=165,
        min_margin=0.1,
        llm_agent=Agent(
            role="Mountain View Agent",
            goal="Get bookings without undercutting brand value",
            backstory="You represent Mountain View Inn, a scenic hotel with great reviews and flexible winter rates.",
            verbose=False,
            llm=llm,  # Pass the LLM directly
        )
    )

    hotels = [hotel1, hotel2, hotel3]
    customer = CustomerAgent(initial_offer=initial_offer)
    customer.negotiate(hotels)
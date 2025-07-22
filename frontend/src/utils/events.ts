import { v4 as uuidv4 } from 'uuid';


type SubscriberID = string;


interface Subscriber {
    getId(): SubscriberID;
    subscribeIfNeeded(element: HTMLElement): void;
    unsubscribeAll(): void;
}


abstract class SubscriberBase {

    private id: SubscriberID;
    private selector: string;

    constructor(id: string, selector: string){
        this.id = id;
        this.selector = selector;
    }

    /**
     * Get the subscriber's ID.
     */
    public getId(): string {
        return this.id;
    }

    /**
     * Subscribe the current element, and any of it's children, if they match the selector.
     */
    public subscribeIfNeeded(element: HTMLElement): void {
        const elementsToSubscribe = this.selectAllIncludingSelf(element);
        for (let element of elementsToSubscribe){
            console.log("Elements matches query selector: ", element, this.selector);
            this.subscribe(element);
        }
    }

    /**
     * Select all HTML elements (including the given element if it matches) using a selector string.
     */
    private selectAllIncludingSelf(element: HTMLElement): Array<HTMLElement> {
        const elements: Array<HTMLElement> = [];
        if (element.matches(this.selector)) {
            elements.push(element);
        }
        for (let node of element.querySelectorAll(this.selector)){
            if (node instanceof HTMLElement){
                elements.push(node);
            }
        }
        return elements;
    }

    /**
     * Subscribe the given HTML element and return it's subscription ID.
     */
    protected abstract subscribe(element: HTMLElement): void;
}


/**
 * Subscribe to changes picked up by an event listener on any existing, or future, 
 * element matching the given node-selector string.
 */
class EventListenerSubscriber extends SubscriberBase implements Subscriber {

    private eventName: string;
    private callback: (e: Event) => void;
    private subscribedElements: Array<HTMLElement>;

    constructor(eventName: string, selector: string, callback: (e: Event) => void){
        super(uuidv4(), selector)
        this.eventName = eventName;
        this.callback = callback;
        this.subscribedElements = [];
    }

    protected subscribe(element: HTMLElement): void {
        element.addEventListener(this.eventName, this.callback);
        this.subscribedElements.push(element);
    }

    public unsubscribeAll(): void {
        for (let element of this.subscribedElements){
            element.removeEventListener(this.eventName, this.callback);
        }
    }

}


/**
 * Subscribe to changes picked up by a mutation observer on any existing, or future, 
 * element matching the given node-selector string.
 */
class MutationObserverSubscriber extends SubscriberBase implements Subscriber {
    
    private observerOptions: MutationObserverInit;
    private callback: (mutation: MutationRecord) => void;
    private observers: Array<MutationObserver>;

    constructor(observerOptions: MutationObserverInit, selector: string, callback: (mutation: MutationRecord) => void){
        super(uuidv4(), selector);
        this.observerOptions = observerOptions;
        this.callback = callback;
        this.observers = [];
    }

    protected subscribe(element: HTMLElement): void {
        const observer = new MutationObserver((mutations: MutationRecord[]) => {
            for (let mutation of mutations){
                this.callback(mutation);
            }
        });
        observer.observe(element, this.observerOptions);
        this.observers.push(observer);
    }
    
    unsubscribeAll(): void {
        for (let observer of this.observers){
            observer.disconnect();
        }
    }

}


/**
 * Provides an interface to declaratively register event listeners and mutation observers 
 * (as "subscriptions") on DOM elements, even if they don't exist yet.
 */
export class DynamicSubscriberManager {
    
    private parentElement: HTMLElement;
    private subscribers: Map<SubscriberID, Subscriber>;
    
    constructor(parentElement: HTMLElement) {
        this.parentElement = parentElement;
        this.subscribers = new Map<SubscriberID, Subscriber>();
        this.initElementAddedObserver();
    }

    /**
     * Initializes an observer on the parent node that fires anytime a new element is added to the DOM.
     */
    private initElementAddedObserver(): void {
        const elementsFromNodeList = (nodes: NodeList): Array<HTMLElement> => {
            const elements: Array<HTMLElement> = [];
            for (let node of nodes){
                if (node instanceof HTMLElement){
                    elements.push(node);
                }
            }
            return elements;
        };
        const handleMutation = (mutation: MutationRecord) => {
            if (mutation.type === 'childList') {
                const elements = elementsFromNodeList(mutation.addedNodes);
                for (let element of elements) {

                    // Each subscriber has the chance to subscribe to changes on the newly added element.
                    for (let subscriber of this.subscribers.values()){
                        subscriber.subscribeIfNeeded(element);
                    }
                }
            }
        };
        const observer = new MutationObserver((mutations) => {
            for (const mutation of mutations) {
                handleMutation(mutation);
            }
        });
        observer.observe(this.parentElement, {
            childList: true,
            subtree: true,
        });
    }

    public subscribeEventListener(eventName: string, selector: string, callback: (event: Event) => void): SubscriberID {
        const subscriber = new EventListenerSubscriber(eventName, selector, callback);
        this.registerSubscriber(subscriber);
        return subscriber.getId();
    }

    public subscribeMutationObserver(observerOptions: MutationObserverInit, selector: string, callback: (mutation: MutationRecord) => void): SubscriberID {
        const subscriber = new MutationObserverSubscriber(observerOptions, selector, callback);
        this.registerSubscriber(subscriber);
        return subscriber.getId();
    }

    private registerSubscriber(subscriber: Subscriber): void {

        // Add subscriptions to any applicable elements at subscriber-creation time.
        subscriber.subscribeIfNeeded(this.parentElement);

        // Track the subscriber so that subscriptions can be dynamically created when a new 
        // element is added to the DOM that matches the given selector.
        this.subscribers.set(subscriber.getId(), subscriber);
    }

    /**
     * Unsubscribe from all of the subscriber's current subscriptions, and stop the subscriber from dynamically creating any new subscriptions. 
     */
    public killSubscriber(id: SubscriberID): boolean {
        const subscriber = this.subscribers.get(id);
        if (subscriber !== undefined){
            subscriber.unsubscribeAll()
            this.subscribers.delete(id);
            return true;
        }
        return false;
    }

}

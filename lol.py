    def announce_payload(self):
        """
        Returns the query params used to announce client to tracker.
        Returns dictionary of query params.
        """
        return {
            "info_hash" : self.torrent.info_hash,
            "peer_id" : self.torrent.peer_id,
            "port" : self.torrent.port,
            "uploaded" : self.torrent.uploaded,
            "downloaded" : self.torrent.downloaded,
            "left" : self.torrent.remaining,
            "compact" : 1
        }

    def announce(self):
        """
        Announces client to tracker and handles response.
        Returns dictionary of peers.
        """

        # Send the request
        try:
            response = requests.get(
                self.tracker_url,
                params=self.announce_payload,
                allow_redirects=False
            )
            logging.debug("Tracker URL: {0}".format(response.url))
        except requests.ConnectionError as e:
            logging.warn(
                "Tracker not found: {0}".format(
                    self.tracker_url
                )
            )
            return {}

        if response.status_code < 200 or response.status_code >= 300:
            raise BitTorrentException(
                "Tracker response error '{0}' for URL: {1}".format(
                    response.content,
                    response.url
                )
            )

        self.last_run = self.now

        decoded_response = Bencode.decode(response.content)

        self.tracker_interval = decoded_response.get(
            'interval',
            self.TRACKER_INTERVAL
        )
        logging.debug("Tracking interval set to: {interval}".format(
            interval=self.tracker_interval
        ))

        if "failure reason" in decoded_response:
            raise BitTorrentException(decoded_response["failure reason"])

        if "peers" in decoded_response: # ignoring `peer6` (ipv6) for now
            peers = decode_binary_peers(decoded_response['peers'])
        else:
            peers = []

        return dict(map(
                lambda hostport: (
                    hostport, self.PEER(hostport, self.torrent)
                ),
                peers
            ))
